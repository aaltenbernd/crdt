from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core import serializers

from .models import *
from .operation import *

from django.conf import settings

def api_register(request):
	if request.method == 'POST':
		username = request.POST['username']
		password = request.POST['password']
		password_confirm = request.POST['password_confirm']

		if password != password_confirm:
			return JsonResponse(dict(error=True, message="Password don't match."))

		createUser(username, password, False, False)

		return JsonResponse(dict(error=False, message="User created."))

	return JsonResponse(dict(error=True, message="No post request."))

def api_login(request):
	if request.method == 'POST':
		username = request.POST.get('username')

		if username is None:
			return JsonResponse(dict(error=True, message="Username is none."))

		password = request.POST.get('password')

		if password is None:
			return JsonResponse(dict(error=True, message="password is none."))

		user = authenticate(username=username, password=password)

		login(request,user)

		if user.is_authenticated():
			return JsonResponse(dict(error=False, message="Logged in."))
		else:
			return JsonResponse(dict(error=True, message="Username is not authenticated."))
	
	return JsonResponse(dict(error=True, message="No post request."))

def api_logout(request):
	logout(request)
	return JsonResponse(dict(error=False, message="Logged out."))

def api_addMessage(request):
	if not request.user.is_authenticated():
		return JsonResponse(dict(error=True, message="User is not authenticated."))

	if request.method == 'POST':
		text = request.POST.get('text')
		username = request.POST.get('reader')
		reader = User.objects.get(username=username)
		reader_uuid = reader.userprofile.uuid
		author = request.user.username
		author_uuid = request.user.userprofile.uuid

		if reader is None:
			return JsonResponse(dict(error=True, message="User don't exist."))

		message = addMessage(text, author, author_uuid, reader, reader_uuid)

		if message is None:
			return JsonResponse(dict(error=True, message="No message added."))
		else:
			return JsonResponse(dict(error=False, message="Added message.", uuid=message.uuid))

	return JsonResponse(dict(error=True, message="No post request."))

def api_deleteMessage(request, message_id):
	if not request.user.is_authenticated():
		return JsonResponse(dict(error=True, message="User is not authenticated."))

	delete_message = deleteMessage(message_id)

	if delete_message is None:
		return JsonResponse(dict(error=True, message="No message deleted."))
	else:
		return JsonResponse(dict(error=False, message="Deleted message.", uuid=delete_message.uuid))

def api_addFolder(request):
	if not request.user.is_authenticated():
		return JsonResponse(dict(error=True, message="User is not authenticated."))

	if request.method == "POST":

		title = request.POST.get('title')

		folder = addFolder(title, request.user.userprofile.uuid)

		if folder is None:
			return JsonResponse(dict(error=True, message="No folder added."))
		else:
			return JsonResponse(dict(error=False, message="Added folder.", uuid=folder.uuid))

	return JsonResponse(dict(error=True, message="No post request."))

def api_deleteFolder(request, folder_id):
	if not request.user.is_authenticated():
		return JsonResponse(dict(error=True, message="User is not authenticated."))

	delete_folder = deleteFolder(folder_id)

	if delete_folder is None:
		return JsonResponse(dict(error=True, message="No folder deleted."))
	else:
		return JsonResponse(dict(error=False, message="Deleted folder.", uuid=delete_folder.uuid))

def api_changeFolder(request, message_id):
	if not request.user.is_authenticated():
		return JsonResponse(dict(error=True, message="User is not authenticated."))

	if request.method == "POST":
		folder_choice = request.POST.get('folder_choice')

		new_message = changeFolder(message_id, folder_choice)

		if new_message is None:
			return JsonResponse(dict(error=True, message="Folder not changed."))
		else:
			return JsonResponse(dict(error=False, message="Changed folder.", uuid=new_message.uuid))

	return JsonResponse(dict(error=True, message="No post request."))


def api_getCurrentState(request):
	if not request.user.is_authenticated():
		return JsonResponse(dict(error=True, message="User is not authenticated."))

	messages = getAllMessages(request.user.userprofile.uuid, 'all_inbox')

	folders = getAllFolders(request.user.userprofile.uuid)

	folder_dict = {}
	for folder in folders:
		folder_dict[str(folder.uuid)] = len(messages.filter(folder_id=str(folder.uuid)))
	
	return JsonResponse(dict(
		error=False, 
		add_messages_count=len(AddMessage.objects.all()), 
		delete_messages_count=len(DeleteMessage.objects.all()), 
		messages_count=len(messages),
		add_folder_count=len(AddFolder.objects.all()),
		delete_folder_count=len(DeleteFolder.objects.all()),
		folders_count=len(folders),
		folder_dict=folder_dict))

def api_getQueue(request):
	if not request.user.is_authenticated():
		return JsonResponse(dict(error=True, message="User is not authenticated."))

	response_dict = {}
	for host in settings.OTHER_HOSTS:
		response_dict[host['id']] = settings.QUEUE[host['id']].qsize()

	print response_dict

	return JsonResponse(response_dict)