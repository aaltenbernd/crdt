import uuid
import time

from django.conf import settings

from .models import *

def addFolder(user_uuid, title):
	"""Refers a new folder to the set manager."""

	start = time.time()

	folder = dict(
		uuid=str(uuid.uuid4()), 
		operation='add_folder', 
		title=title, 
		user_id=str(user_uuid)
	)

	settings.SET_MANAGER.add(folder, True)

	return time.time() - start

def addMessage(text, author_id, reader_id):
	"""Refers a new message (inbox and outbox) to the set manager."""

	start = time.time()

	date = time.strftime("%b %d %Y %H:%M:%S")

	inbox_message = dict(
		uuid=str(uuid.uuid4()), 
		date=date, 
		operation='add', 
		text=text, 
		author_id=str(author_id), 
		reader_id=str(reader_id), 
		host=settings.RUNNING_HOST['id']
	)

	settings.SET_MANAGER.add(inbox_message, True)
	
	'''outbox_message = dict(
		uuid=str(uuid.uuid4()), 
		date=date, 
		operation='add_outbox', 
		text=text, 
		author_id=str(author_id), 
		reader_id=str(reader_id), 
		host=settings.RUNNING_HOST['id']
	)

	settings.SET_MANAGER.add(outbox_message, True)'''

	return time.time() - start

def deleteOutboxMessage(uuid):
	"""Refers a delete outbox message to the set manager."""

	start = time.time()

	delete_message = dict(
		operation='delete', 
		uuid=str(uuid)
	)

	settings.SET_MANAGER.add(delete_message, True)

	return time.time() - start

def deleteMessage(uuid):
	"""Refers a delete message to the set manager."""

	start = time.time()

	delete_message = dict(
		operation='delete', 
		uuid=str(uuid)
	)

	settings.SET_MANAGER.add(delete_message, True)

	return time.time() - start

def deleteFolder(uuid):
	"""Refers a delete folder to the set manager."""

	start = time.time()
	
	delete_folder = dict(
		operation='delete_folder', 
		uuid=str(uuid)
	)
	
	settings.SET_MANAGER.add(delete_folder, True)

	return time.time() - start

def changeFolder(message_id, old_folder, new_folder):
	"""
	Refers a change folder to the set manager:
		inbox  to folder => add message to folder
		folder to inbox  => delete message and add new message
		folder to folder =>
			1st case (uuid is smaller):
				add message to folder
			2nd case (uuid is bigger):
				delete message, add new message and add message to folder
	"""

	start = time.time()

	# return if message don't exist
	try:
		add_message = settings.SET_MANAGER.getMessage(message_id)
	except:
		return time.time() - start

	# return if same folders
	if old_folder == new_folder:
		return time.time() - start

	# inbox to folder
	if old_folder == 'Inbox' and new_folder != 'Inbox':

		new_message = dict(
			uuid=str(add_message.uuid), 
			operation='add_to_folder', 
			folder_id=str(new_folder), 
			text=add_message.text, 
			host=add_message.host, 
			date=add_message.date, 
			author_id=str(add_message.author_id), 
			reader_id=str(add_message.reader_id)
		)

		settings.SET_MANAGER.add(new_message, True)

	else:
		# folder to inbox
		if new_folder == 'Inbox':

			delete_message = dict(
				operation='delete', 
				uuid=str(message_id)
			)

			settings.SET_MANAGER.add(delete_message, True)

			new_message = dict(
				uuid=str(uuid.uuid4()), 
				operation='add', 
				text=add_message.text, 
				host=add_message.host, 
				date=add_message.date, 
				author_id=str(add_message.author_id), 
				reader_id=str(add_message.reader_id)
			)

			settings.SET_MANAGER.add(new_message, True)

		# folder to folder
		else:

			# return if folder don't exist
			try:
				old_f = settings.SET_MANAGER.getFolder(old_folder)
				new_f = settings.SET_MANAGER.getFolder(new_folder)
			except:
				return time.time() - start

			# 1st case
			if hash(new_f) > hash(old_f):
				
				new_message = dict(
					uuid=str(add_message.uuid), 
					operation='add_to_folder', 
					folder_id=str(new_folder), 
					text=add_message.text, 
					host=add_message.host, 
					date=add_message.date, 
					author_id=str(add_message.author_id), 
					reader_id=str(add_message.reader_id)
				)

				settings.SET_MANAGER.add(new_message, True)

			# 2nd case
			else:
				
				delete_message = dict(
					operation='delete', 
					uuid=str(message_id)
				)
				
				settings.SET_MANAGER.add(delete_message, True)
				
				new_message = dict(
					uuid=str(uuid.uuid4()), 
					operation='add_to_folder', 
					folder_id=str(new_folder), 
					need_add=True, 
					text=add_message.text, 
					host=add_message.host, 
					date=add_message.date, 
					author_id=str(add_message.author_id), 
					reader_id=str(add_message.reader_id)
				)

				settings.SET_MANAGER.add(new_message, True)

	return time.time() - start

def markRead(message_id):
	"""Refers new read marker to the set manager."""
	
	start = time.time()
	
	try:
		# can't mark read if message is allready read
		if settings.SET_MANAGER.messageRead(message_id) == True:
			return time.time() - start

		# block while flatten
		while settings.FLAT_MANAGER.getFlat():
			time.sleep(1)

		new_marker = dict(
			uuid=str(message_id), 
			operation='markRead', 
			number=settings.SET_MANAGER.mark[str(message_id)][0]
		)
		
		settings.SET_MANAGER.add(new_marker, True)
	except:
		return time.time() - start

	return time.time() - start

def markUread(message_id):
	"""Refers new unread marker to the set manager."""

	start = time.time()

	try:
		# can't mark unread if message is allready unread
		if settings.SET_MANAGER.messageRead(message_id) == False:
			return time.time() - start

		# block while flatten
		while settings.FLAT_MANAGER.getFlat():
			time.sleep(1)

		new_marker = dict(
			uuid=str(message_id), 
			operation='markUnread', 
			number=settings.SET_MANAGER.mark[str(message_id)][1]
		)
		
		settings.SET_MANAGER.add(new_marker, True)
	except:
		return time.time() - start

	return time.time() - start

def getAllOutboxMessages(user_id, mark):
	"""
	Returns messages in the outbox.
	With the given mark specification (read, unread, all).
	"""

	outbox = settings.SET_MANAGER.getOutbox()

	if mark == 'all':
		return [
			msg for msg in outbox 
			if msg.author_id == user_id
		]
	if mark == 'read':
		return [
			msg for msg in outbox 
			if msg.author_id == user_id 
			and settings.SET_MANAGER.messageRead(msg.uuid) == True
		]
	if mark == 'unread':
		return [
			msg for msg in outbox 
			if msg.author_id == user_id 
			and settings.SET_MANAGER.messageRead(msg.uuid) == False
		]

def getAllInboxMessages(user_id, mark):
	"""
	Returns messages in the inbox.
	With the given mark specification (read, unread, all).
	"""

	inbox = settings.SET_MANAGER.getInbox()

	if mark == 'all':
		return [
			msg for msg in inbox 
			if msg.reader_id == user_id
		]
	if mark == 'read':
		return [
			msg for msg in inbox if msg.reader_id == user_id 
			and settings.SET_MANAGER.messageRead(msg.uuid) == True
		]
	if mark == 'unread':
		return [
			msg for msg in inbox 
			if msg.reader_id == user_id 
			and settings.SET_MANAGER.messageRead(msg.uuid) == False
		]

def getAllMessages(user_id, mark):
	"""
	Returns all messages.
	With the given mark specification (read, unread, all).
	"""

	messages = settings.SET_MANAGER.getMessages()

	if mark == 'all':
		return [
			msg for msg in messages
			if msg.reader_id
		]
	if mark == 'read':
		return [
			msg for msg in messages 
			if msg.reader_id == user_id 
			and settings.SET_MANAGER.messageRead(msg.uuid) == True
		]
	if mark == 'unread':
		return [
			msg for msg in messages 
			if msg.reader_id == user_id 
			and settings.SET_MANAGER.messageRead(msg.uuid) == False
		]

def getAllMessagesInFolder(user_id, folder, mark):
	"""
	Returns messages in the given folder.
	With the given mark specification (read, unread, all).
	"""

	messages = settings.SET_MANAGER.getInFolder(folder)

	if mark == 'all':
		return [
			msg for msg in messages 
			if msg.reader_id == user_id
		]
	if mark == 'read':
		return [
			msg for msg in messages 
			if msg.reader_id == user_id 
			and settings.SET_MANAGER.messageRead(msg.uuid) == True
		]
	if mark == 'unread':
		return [
			msg for msg in messages 
			if msg.reader_id == user_id 
			and settings.SET_MANAGER.messageRead(msg.uuid) == False
		]

def getAllFolders(user_id):
	"""Returns all folder."""

	folders = settings.SET_MANAGER.getFolders()

	return [f for f in folders if f.user_id == user_id]

def createUser(username, password):
	"""
	Creates a user with given username and password.
	Afterwards distributing the new user to the other hosts.
	"""

	user = User.objects.filter(username=username)

	if user:
		return user.first().userprofile.uuid 

	user = User.objects.create_user(
		username=username, 
		password=password, 
		is_staff=True, 
		is_superuser=True
	)

	profile = UserProfile.objects.create(
		uuid=uuid.uuid4(), 
		user=user, 
		password=password
	)

	user.userprofile = profile
	user.save()

	for host in settings.OTHER_HOSTS:
		settings.SENDER[host['id']].queue.put(
			dict(
				uuid=str(user.userprofile.uuid), 
				username=username, 
				password=password, 
				operation='add_user')
			)
 	
 	return user.userprofile.uuid