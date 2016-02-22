from .models import *

from django.conf import settings
import uuid
import time
import sys

def addFolder(user_uuid, title):
	op_start = time.time()
	folder = dict(uuid=str(uuid.uuid4()), operation='add_folder', title=title, user_id=str(user_uuid))

	settings.SET_MANAGER.add(folder, True)

	return (folder['uuid'], (time.time() - op_start))

def addMessage(user_uuid, text, author_id, reader_id):
	op_start = time.time()
	date = time.strftime("%b %d %Y %H:%M:%S")
	inbox_message = dict(uuid=str(uuid.uuid4()), date=date, operation='add', text=text, author_id=str(author_id), reader_id=str(reader_id), folder=None, host=settings.RUNNING_HOST['id'])
	outbox_message = dict(uuid=str(uuid.uuid4()), date=date, operation='add_outbox', text=text, author_id=str(author_id), reader_id=str(reader_id), host=settings.RUNNING_HOST['id'])

	settings.SET_MANAGER.add(inbox_message, True)
	settings.SET_MANAGER.add(outbox_message, True)

	return (inbox_message['uuid'], (time.time() - op_start))

def deleteOutboxMessage(user_uuid, uuid):
	#for outbox_message in settings.SET_MANAGER.getOutboxMessages():
	#	if str(add_message.uuid) == uuid:
	#		break
	#else:
	#	return None

	op_start = time.time()

	delete_message = dict(operation='delete', uuid=str(uuid))
	settings.SET_MANAGER.add(delete_message, True)

	return (delete_message['uuid'], (time.time() - op_start))

def deleteMessage(user_uuid, uuid):
	#for message in settings.SET_MANAGER.getMessages():
	#	if str(message.uuid) == uuid:
	#		break
	#else:
	#	return None
	op_start = time.time()

	delete_message = dict(operation='delete', uuid=str(uuid))
	settings.SET_MANAGER.add(delete_message, True)

	return (delete_message['uuid'], (time.time() - op_start))



def deleteFolder(user_id, uuid):
	#for add_folder in settings.SET_MANAGER.getFolders():
	#	if str(add_folder.uuid) == uuid:
	#		break
	#else:
	#	return None

	op_start = time.time()
	delete_folder = dict(operation='delete_folder', uuid=str(uuid))
	settings.SET_MANAGER.add(delete_folder, True)

	# Muessen wirklich alle Nachrichten geloescht werden?

	#messages = getAllMessages(user_id, add_folder.uuid)

	#for add_message in messages:
	#	delete_message = dict(operation='delete', uuid=add_message.uuid)
	#	settings.SET_MANAGER.add(delete_message, True)

	return (delete_folder['uuid'], (time.time() - op_start))

def changeFolder(user_uuid, message_id, folder_choice, by_uuid):
	op_start = time.time()

	for add_message in settings.SET_MANAGER.getMessages():
		if str(add_message.uuid) == message_id:
			break
	else:
		return None

	if folder_choice != 'Inbox':
		if not by_uuid:
			for folder in settings.SET_MANAGER.getFolders():
				if folder.title == folder_choice:
					break
			else:
				return None
			folder_choice = folder.uuid

		folder_choice = str(folder_choice)
	else:
		folder_choice = None
	
	delete_message = dict(operation='delete', uuid=str(message_id))
	settings.SET_MANAGER.add(delete_message, True)

	new_message = dict(uuid=str(uuid.uuid4()), operation='add', text=add_message.text, host=add_message.host, folder=folder_choice, date=add_message.date, author_id=str(add_message.author_id), reader_id=str(add_message.reader_id))
	settings.SET_MANAGER.add(new_message, True)

	return (new_message['uuid'], (time.time() - op_start))

def getAllOutboxMessages(user_id):
	outbox = settings.SET_MANAGER.getOutboxMessages()
	return [msg for msg in outbox if msg.author_id == user_id]

def getAllMessages(user_id):
	messages = settings.SET_MANAGER.getMessages()
	return [msg for msg in messages if msg.reader_id == user_id]

def getAllMessagesInFolder(user_id, folder):
	messages = settings.SET_MANAGER.getMessages()
	return [msg for msg in messages if msg.reader_id == user_id and msg.folder == folder]

def getAllFolders(user_id):
	folders = settings.SET_MANAGER.getFolders()
	return [f for f in folders if f.user_id == user_id]

def createUser(username, password):
	user = User.objects.filter(username=username)
	if user:
		return user.first().userprofile.uuid 
	user = User.objects.create_user(username=username, password=password, is_staff=True, is_superuser=True)
	profile = UserProfile.objects.create(uuid=uuid.uuid4(), user=user)
	user.userprofile = profile

	for host in settings.OTHER_HOSTS:
		settings.QUEUE[host['id']].put(dict(uuid=str(user.userprofile.uuid), username=username, password=password, operation='add_user'))
 	return user.userprofile.uuid