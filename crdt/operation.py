from .models import *

from django.conf import settings

def addMessage(text, author, author_uuid, reader, reader_uuid):

	inbox_message = AddMessage.objects.create(text=text, author=author, author_uuid=author_uuid, reader=reader, reader_uuid=reader_uuid, folder_id=None, host_id=settings.RUNNING_HOST['id'], inbox=True)
	outbox_message = AddMessage.objects.create(text=text, author=author, author_uuid=author_uuid, reader=reader, reader_uuid=reader_uuid, folder_id=None, host_id=settings.RUNNING_HOST['id'], inbox=False)

	for host in settings.OTHER_HOSTS:
		settings.QUEUE[host['id']].put(inbox_message.to_dict())
		settings.QUEUE[host['id']].put(outbox_message.to_dict())

	return inbox_message

def deleteMessage(uuid):
	add_message = AddMessage.objects.get(uuid=uuid)

	if add_message is None:
		return None

	delete_message = DeleteMessage.objects.create(uuid=add_message.uuid, host_id=add_message.host_id, author=add_message.author, author_uuid=add_message.author_uuid, reader=add_message.reader, reader_uuid=add_message.reader_uuid)

	for host in settings.OTHER_HOSTS:
		settings.QUEUE[host['id']].put(delete_message.to_dict())

	return delete_message

def addFolder(title, user_uuid):
	folder = AddFolder.objects.create(title=title, host_id=settings.RUNNING_HOST['id'], user_uuid=user_uuid)

	for host in settings.OTHER_HOSTS:
		settings.QUEUE[host['id']].put(folder.to_dict())

	return folder

def deleteFolder(folder_id):
	add_folder = AddFolder.objects.get(uuid=folder_id)

	if add_folder == None:
		return None

	delete_folder = DeleteFolder.objects.create(uuid=add_folder.uuid, host_id=add_folder.host_id, user_uuid=add_folder.user_uuid)

	for host in settings.OTHER_HOSTS:
		settings.QUEUE[host['id']].put(delete_folder.to_dict())

	messages = AddMessage.objects.all()
	for delete_message in DeleteMessage.objects.all():
		messages = messages.exclude(uuid=delete_message.uuid)

	messages = messages.filter(folder_id=add_folder.uuid)
	for add_message in messages:
		delete_message = DeleteMessage.objects.create(uuid=add_message.uuid, host_id=add_message.host_id, author=add_message.author, author_uuid=add_message.author_uuid, reader=add_message.reader, reader_uuid=add_message.reader_uuid)
		for host in settings.OTHER_HOSTS:
			settings.QUEUE[host['id']].put(delete_message.to_dict())

	return delete_folder

def changeFolder(message_id, folder_choice):
	if not folder_choice:
		folder_choice = None

	add_message = AddMessage.objects.get(uuid=message_id)

	if add_message is None:
		return None

	if str(add_message.folder_id) == str(folder_choice):
		return None
	
	delete_message = DeleteMessage.objects.create(uuid=add_message.uuid, host_id=add_message.host_id, author=add_message.author, author_uuid=add_message.author_uuid, reader=add_message.reader, reader_uuid=add_message.reader_uuid)

	new_message = AddMessage.objects.create(text=add_message.text, host_id=add_message.host_id, folder_id=folder_choice, date=add_message.date, author=add_message.author, author_uuid=add_message.author_uuid, reader=add_message.reader, reader_uuid=add_message.reader_uuid, inbox=True)

	for host in settings.OTHER_HOSTS:
		settings.QUEUE[host['id']].put(delete_message.to_dict())
		settings.QUEUE[host['id']].put(new_message.to_dict())

	return new_message

def getAllMessages(user_uuid, active_folder_id):
    if active_folder_id == 'inbox':
        messages = AddMessage.objects.filter(reader_uuid=user_uuid).filter(inbox=True).filter(folder_id=None)
        for delete_message in DeleteMessage.objects.filter(reader_uuid=user_uuid):
            messages = messages.exclude(uuid=delete_message.uuid)
    elif active_folder_id == 'all_inbox':
    	messages = AddMessage.objects.filter(reader_uuid=user_uuid).filter(inbox=True)
        for delete_message in DeleteMessage.objects.filter(reader_uuid=user_uuid):
            messages = messages.exclude(uuid=delete_message.uuid)
    elif active_folder_id == 'outbox':
        messages = AddMessage.objects.filter(author_uuid=user_uuid).filter(inbox=False)
        for delete_message in DeleteMessage.objects.filter(author_uuid=user_uuid):
            messages = messages.exclude(uuid=delete_message.uuid)
    else:
        messages = AddMessage.objects.filter(reader_uuid=user_uuid).filter(inbox=True).filter(folder_id=active_folder_id)
        for delete_message in DeleteMessage.objects.filter(reader_uuid=user_uuid):
            messages = messages.exclude(uuid=delete_message.uuid)

    return messages

def getAllFolders(user_uuid):
    folders = AddFolder.objects.filter(user_uuid=user_uuid)
    for delete_folder in DeleteFolder.objects.filter(user_uuid=user_uuid):
        folders = folders.exclude(uuid=delete_folder.uuid)

    return folders

def createUser(username, password, is_staff, is_superuser):
	user = User.objects.create_user(username=username, password=password, is_staff=is_staff, is_superuser=is_superuser)
	profile = UserProfile.objects.create(user=user)
	user.userprofile = profile
	user_dict = {}
	user_dict['uuid'] = user.userprofile.uuid
	user_dict['username'] = username
	user_dict['password'] = password
	user_dict['is_staff'] = is_staff
	user_dict['is_superuser'] = is_superuser
	user_dict['operation'] = 'add_user'

	for host in settings.OTHER_HOSTS:
		settings.QUEUE[host['id']].put(user_dict)
 	return