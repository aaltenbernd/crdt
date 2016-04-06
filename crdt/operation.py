import uuid
import time

from .models import *
from django.conf import settings

def addFolder(user_uuid, title):
	start = time.time()
	folder = dict(uuid=str(uuid.uuid4()), operation='add_folder', title=title, user_id=str(user_uuid))

	settings.SET_MANAGER.add(folder, True)

	return time.time() - start

def addMessage(user_uuid, text, author_id, reader_id):
	start = time.time()
	date = time.strftime("%b %d %Y %H:%M:%S")
	inbox_message = dict(uuid=str(uuid.uuid4()), date=date, operation='add', text=text, author_id=str(author_id), reader_id=str(reader_id), host=settings.RUNNING_HOST['id'])
	outbox_message = dict(uuid=str(uuid.uuid4()), date=date, operation='add_outbox', text=text, author_id=str(author_id), reader_id=str(reader_id), host=settings.RUNNING_HOST['id'])

	settings.SET_MANAGER.add(inbox_message, True)
	settings.SET_MANAGER.add(outbox_message, True)

	return time.time() - start

def deleteOutboxMessage(user_uuid, uuid):
	start = time.time()
	delete_message = dict(operation='delete', uuid=str(uuid))
	settings.SET_MANAGER.add(delete_message, True)

	return time.time() - start

def deleteMessage(user_uuid, uuid):
	start = time.time()
	delete_message = dict(operation='delete', uuid=str(uuid))
	settings.SET_MANAGER.add(delete_message, True)

	return time.time() - start

def deleteFolder(user_id, uuid):
	start = time.time()
	delete_folder = dict(operation='delete_folder', uuid=str(uuid))
	settings.SET_MANAGER.add(delete_folder, True)

	return time.time() - start

def changeFolder(user_id, message_id, old_folder, new_folder):
	start = time.time()
	try:
		add_message = settings.SET_MANAGER.getMessage(message_id)
	except:
		return time.time() - start

	if old_folder == new_folder:
		return time.time() - start

	if old_folder == 'Inbox' and new_folder != 'Inbox':
		new_message = dict(uuid=str(add_message.uuid), operation='add_to_folder', folder_id=str(new_folder), text=add_message.text, host=add_message.host, date=add_message.date, author_id=str(add_message.author_id), reader_id=str(add_message.reader_id))
		settings.SET_MANAGER.add(new_message, True)
	else:
		if new_folder == 'Inbox':
			delete_message = dict(operation='delete', uuid=str(message_id))
			settings.SET_MANAGER.add(delete_message, True)
			new_message = dict(uuid=str(uuid.uuid4()), operation='add', text=add_message.text, host=add_message.host, date=add_message.date, author_id=str(add_message.author_id), reader_id=str(add_message.reader_id))
			settings.SET_MANAGER.add(new_message, True)
		else:
			try:
				old_f = settings.SET_MANAGER.getFolder(old_folder)
				new_f = settings.SET_MANAGER.getFolder(new_folder)
			except:
				return time.time() - start

			if hash(new_f) > hash(old_f):
				new_message = dict(uuid=str(add_message.uuid), operation='add_to_folder', folder_id=str(new_folder), text=add_message.text, host=add_message.host, date=add_message.date, author_id=str(add_message.author_id), reader_id=str(add_message.reader_id))
				settings.SET_MANAGER.add(new_message, True)
			else:
				delete_message = dict(operation='delete', uuid=str(message_id))
				settings.SET_MANAGER.add(delete_message, True)
				new_message = dict(uuid=str(uuid.uuid4()), operation='add_to_folder', folder_id=str(new_folder), need_add=True, text=add_message.text, host=add_message.host, date=add_message.date, author_id=str(add_message.author_id), reader_id=str(add_message.reader_id))
				settings.SET_MANAGER.add(new_message, True)

	return time.time() - start

def mark_readed(user_id, message_id):
	start = time.time()
	try:
		if settings.SET_MANAGER.messageReaded(message_id) == True:
			return time.time() - start
	except:
		return time.time() - start

	while settings.FLAT_MANAGER.getFlat():
		time.sleep(1)

	new_marker = dict(uuid=str(message_id), operation='mark_readed', number=settings.SET_MANAGER.mark[str(message_id)][0])
	settings.SET_MANAGER.add(new_marker, True)

	return time.time() - start

def mark_unreaded(user_id, message_id):
	start = time.time()
	try:
		if settings.SET_MANAGER.messageReaded(message_id) == False:
			return time.time() - start
	except:
		return time.time() - start

	while settings.FLAT_MANAGER.getFlat():
		time.sleep(1)

	new_marker = dict(uuid=str(message_id), operation='mark_un_readed', number=settings.SET_MANAGER.mark[str(message_id)][1])
	settings.SET_MANAGER.add(new_marker, True)

	return time.time() - start

def getAllOutboxMessages(user_id, mark):
	outbox = settings.SET_MANAGER.getOutbox()
	if mark == 'all':
		return [msg for msg in outbox if msg.author_id == user_id]
	if mark == 'readed':
		return [msg for msg in outbox if msg.author_id == user_id and settings.SET_MANAGER.messageReaded(msg.uuid) == True]
	if mark == 'unreaded':
		return [msg for msg in outbox if msg.author_id == user_id and settings.SET_MANAGER.messageReaded(msg.uuid) == False]

def getAllInboxMessages(user_id, mark):
	inbox = settings.SET_MANAGER.getInbox()
	if mark == 'all':
		return [msg for msg in inbox if msg.reader_id == user_id]
	if mark == 'readed':
		return [msg for msg in inbox if msg.reader_id == user_id and settings.SET_MANAGER.messageReaded(msg.uuid) == True]
	if mark == 'unreaded':
		return [msg for msg in inbox if msg.reader_id == user_id and settings.SET_MANAGER.messageReaded(msg.uuid) == False]

def getAllMessages(user_id, mark):
	messages = settings.SET_MANAGER.getMessages()
	if mark == 'all':
		return [msg for msg in messages if msg.reader_id]
	if mark == 'readed':
		return [msg for msg in messages if msg.reader_id == user_id and settings.SET_MANAGER.messageReaded(msg.uuid) == True]
	if mark == 'unreaded':
		return [msg for msg in messages if msg.reader_id == user_id and settings.SET_MANAGER.messageReaded(msg.uuid) == False]

def getAllMessagesInFolder(user_id, folder, mark):
	messages = settings.SET_MANAGER.getInFolder(folder)
	if mark == 'all':
		return [msg for msg in messages if msg.reader_id == user_id]
	if mark == 'readed':
		return [msg for msg in messages if msg.reader_id == user_id and settings.SET_MANAGER.messageReaded(msg.uuid) == True]
	if mark == 'unreaded':
		return [msg for msg in messages if msg.reader_id == user_id and settings.SET_MANAGER.messageReaded(msg.uuid) == False]

def getAllFolders(user_id):
	folders = settings.SET_MANAGER.getFolders()
	return [f for f in folders if f.user_id == user_id]

def createUser(username, password):
	user = User.objects.filter(username=username)
	if user:
		return user.first().userprofile.uuid 
	user = User.objects.create_user(username=username, password=password, is_staff=True, is_superuser=True)
	profile = UserProfile.objects.create(uuid=uuid.uuid4(), user=user, password=password)
	user.userprofile = profile
	user.save()

	for host in settings.OTHER_HOSTS:
		settings.QUEUE[host['id']].put(dict(uuid=str(user.userprofile.uuid), username=username, password=password, operation='add_user'))
 	return user.userprofile.uuid