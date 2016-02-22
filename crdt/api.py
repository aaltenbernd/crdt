from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core import serializers

from .models import *
from .operation import *

import json
import time

from django.conf import settings

def api_register(request):
	if request.method == 'POST':
		username = request.POST['username']
		password = request.POST['password']
		password_confirm = request.POST['password_confirm']

		if password != password_confirm:
			return JsonResponse(dict(error=True, message="Password don't match."))

		uuid = createUser(username, password)

		return JsonResponse(dict(error=False, message="User created / or allready exist.", uuid=str(uuid)))

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
	op_start = time.time()
	if not request.user.is_authenticated():
		return JsonResponse(dict(error=True, message="User is not authenticated."))
	op_end = time.time() - op_start
	print "authentication time .%12f" % op_end

	if request.method == 'POST':
		text = request.POST.get('text')
		reader = request.POST.get('reader')
		reader_user = User.objects.get(username=reader)
		reader_uuid = reader_user.userprofile.uuid
		author_uuid = request.user.userprofile.uuid

		if reader is None:
			return JsonResponse(dict(error=True, message="User don't exist."))

		message = addMessage(request.user.userprofile.uuid, text, author_uuid, reader_uuid)

		if message is None:
			return JsonResponse(dict(error=True, message="No message added."))
		else:			
			return JsonResponse(dict(error=False, message="Added message.", uuid=message[0], time=message[1]))

	return JsonResponse(dict(error=True, message="No post request."))

def api_deleteMessage(request, message_id):
	if not request.user.is_authenticated():
		return JsonResponse(dict(error=True, message="User is not authenticated."))

	delete_message = deleteMessage(request.user.userprofile.uuid, message_id)

	if delete_message is None:
		return JsonResponse(dict(error=True, message="No message deleted."))
	else:
		return JsonResponse(dict(error=False, message="Deleted message.", uuid=delete_message[0], time=delete_message[1]))

def api_addFolder(request):
	if not request.user.is_authenticated():
		return JsonResponse(dict(error=True, message="User is not authenticated."))

	if request.method == "POST":

		title = request.POST.get('title')

		folder = addFolder(request.user.userprofile.uuid, title)

		if folder is None:
			return JsonResponse(dict(error=True, message="No folder added."))
		else:
			return JsonResponse(dict(error=False, message="Added folder.", uuid=folder[0], time=folder[1]))

	return JsonResponse(dict(error=True, message="No post request."))

def api_deleteFolder(request, folder_id):
	if not request.user.is_authenticated():
		return JsonResponse(dict(error=True, message="User is not authenticated."))

	delete_folder = deleteFolder(request.user.userprofile.uuid, folder_id)

	if delete_folder is None:
		return JsonResponse(dict(error=True, message="No folder deleted."))
	else:
		return JsonResponse(dict(error=False, message="Deleted folder.", uuid=delete_folder[0], time=delete_folder[1]))

def api_changeFolder(request, message_id):
	if not request.user.is_authenticated():
		return JsonResponse(dict(error=True, message="User is not authenticated."))

	if request.method == "POST":
		folder_choice = request.POST.get('folder_choice')

		new_message = changeFolder(request.user.userprofile.uuid, message_id, folder_choice, True)

		if new_message is None:
			return JsonResponse(dict(error=True, message="Folder not changed."))
		else:
			return JsonResponse(dict(error=False, message="Changed folder.", uuid=new_message[0], time=new_message[1]))

	return JsonResponse(dict(error=True, message="No post request."))

def api_getMessages(request):
	return JsonResponse([str(msg.uuid) for msg in getAllMessages(request.user.userprofile.uuid)], safe=False)

def api_getFolders(request):
	return JsonResponse([str(fol.uuid) for fol in getAllFolders(request.user.userprofile.uuid)], safe=False)

def api_getState(request):
	data = {}
	data['outbox_messages'] = [str(msg.uuid) for msg in settings.SET_MANAGER.getOutboxMessages()]
	data['add_messages'] = [(str(msg.folder), str(msg.uuid)) for msg in settings.SET_MANAGER.getAddMessages()]
	data['delete_messages'] = [str(msg.uuid) for msg in settings.SET_MANAGER.getDeleteMessages()]
	data['add_folders'] = [str(fol.uuid) for fol in settings.SET_MANAGER.getAddFolders()]
	data['delete_folders'] = [str(fol.uuid) for fol in settings.SET_MANAGER.getDeleteFolders()]
	return JsonResponse(data)

def api_getQueue(request):
	if not request.user.is_authenticated():
		return JsonResponse(dict(error=True, message="User is not authenticated."))

	for host in settings.OTHER_HOSTS:
		if settings.QUEUE[host['id']].qsize() > 0:
			queue = True
			break
	else:
		queue = False

	return JsonResponse(queue, safe=False)

def api_getSetManagerQueue(request):
	if not request.user.is_authenticated():
		return JsonResponse(dict(error=True, message="User is not authenticated."))

	if settings.SET_MANAGER.queue.qsize() > 0:
			queue = True
	else:
		queue = False

	print queue

	return JsonResponse(queue, safe=False)

def api_getSendTime(request):
	if not request.user.is_authenticated():
		return JsonResponse(dict(error=True, message="User is not authenticated."))

	time = 0
	count = 0
	for host in settings.OTHER_HOSTS:
		time += settings.SEND_TIME[host['id']]
		count += 1

	if count > 0:
		time = float(time)/float(count)

	return JsonResponse(dict(error=False, time=time))

