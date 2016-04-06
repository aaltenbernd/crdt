import json

from django.http import HttpResponseForbidden, HttpResponseNotFound, HttpResponseBadRequest, HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.conf import settings
from .models import *
from .operation import *

def api_register(request):
	if request.method == 'POST':
		username = request.POST['username']
		password = request.POST['password']
		password_confirm = request.POST['password_confirm']

		if password != password_confirm:
			return HttpResponseBadRequest()

		createUser(username, password)

		return HttpResponse(status=200)

	return HttpResponseNotFound()

def api_login(request):
	if request.method == 'POST':
		username = request.POST.get('username')

		if username is None:
			return HttpResponseBadRequest()

		password = request.POST.get('password')

		if password is None:
			return HttpResponseBadRequest()

		user = authenticate(username=username, password=password)

		try:
			login(request,user)
		except:
			return HttpResponseForbidden()

		if user.is_authenticated():
			return HttpResponse(status=200)
		else:
			return HttpResponseForbidden()
	
	return HttpResponseNotFound()

def api_logout(request):
	logout(request)
	return HttpResponse(status=200)

def api_addMessage(request):
	if not request.user.is_authenticated():
		return HttpResponseForbidden()

	if request.method == 'POST':
		text = request.POST.get('text')
		reader = request.POST.get('reader')
		reader_user = User.objects.get(username=reader)
		reader_uuid = reader_user.userprofile.uuid
		author_uuid = request.user.userprofile.uuid

		if reader is None:
			return HttpResponseBadRequest()

		time = addMessage(request.user.userprofile.uuid, text, author_uuid, reader_uuid)

		if time is None:
			return HttpResponseBadRequest()
		else:			
			return JsonResponse(dict(time=time))

	return HttpResponseNotFound()

def api_deleteMessage(request):
	if not request.user.is_authenticated():
		return HttpResponseForbidden()

	if request.method == 'POST':
		message_id = request.POST.get('message_id')

		time = deleteMessage(request.user.userprofile.uuid, message_id)

		if time is None:
			return HttpResponseBadRequest()
		else:
			return JsonResponse(dict(time=time))

	return HttpResponseNotFound()

def api_addFolder(request):
	if not request.user.is_authenticated():
		return HttpResponseForbidden()

	if request.method == "POST":

		title = request.POST.get('title')

		time = addFolder(request.user.userprofile.uuid, title)

		if time is None:
			return HttpResponseBadRequest()
		else:
			return JsonResponse(dict(time=time))

	return HttpResponseNotFound()

def api_deleteFolder(request):
	if not request.user.is_authenticated():
		return HttpResponseForbidden()

	if request.method == "POST":
		folder_id = request.POST.get('folder_id')

		time = deleteFolder(request.user.userprofile.uuid, folder_id)

		if time is None:
			return HttpResponseBadRequest()
		else:
			return JsonResponse(dict(time=time))

	return HttpResponseNotFound()

def api_changeFolder(request):
	if not request.user.is_authenticated():
		return HttpResponseForbidden()

	if request.method == "POST":
		message_id = request.POST.get('message_id')
		folder_choice = request.POST.get('folder_choice')
		old_folder = request.POST.get('old_folder')

		time = changeFolder(request.user.userprofile.uuid, message_id, old_folder, folder_choice)

		if time is None:
			return HttpResponseBadRequest()
		else:
			return JsonResponse(dict(time=time))

	return HttpResponseNotFound()

def api_mark_readed(request):
	if not request.user.is_authenticated():
		return HttpResponseForbidden()

	if request.method == "POST":
		message_id = request.POST.get('message_id')

		time = mark_readed(request.user.userprofile.uuid, message_id)

		return JsonResponse(dict(time=time))

	return HttpResponseNotFound()

def api_mark_unreaded(request):
	if not request.user.is_authenticated():
		return HttpResponseForbidden()

	if request.method == "POST":
		message_id = request.POST.get('message_id')

		time = mark_unreaded(request.user.userprofile.uuid, message_id)

		return JsonResponse(dict(time=time))

	return HttpResponseNotFound()

def api_getOutbox(request):
	if not request.user.is_authenticated():
		return HttpResponseForbidden()

	return JsonResponse([str(msg.uuid) for msg in settings.SET_MANAGER.getOutbox()], safe=False)

def api_getInbox(request):
	if not request.user.is_authenticated():
		return HttpResponseForbidden()

	return JsonResponse([str(msg.uuid) for msg in settings.SET_MANAGER.getInbox()], safe=False)

def api_getFolders(request):
	if not request.user.is_authenticated():
		return HttpResponseForbidden()

	return JsonResponse([str(fol.uuid) for fol in settings.SET_MANAGER.getFolders()], safe=False)

def api_getInFolder(request):
	if not request.user.is_authenticated():
		return HttpResponseForbidden()

	if request.method == "POST":
		folder_id = request.POST.get('folder_id')

		return JsonResponse([str(msg.uuid) for msg in settings.SET_MANAGER.getInFolder(str(folder_id))], safe=False)

	return HttpResponseNotFound()

def api_getAllMessages(request):
	if not request.user.is_authenticated():
		return HttpResponseForbidden()

	return JsonResponse([str(msg.uuid) for msg in getAllMessages(request.user.userprofile.uuid, 'all')], safe=False)

def api_getReadedMessages(request):
	if not request.user.is_authenticated():
		return HttpResponseForbidden()

	return JsonResponse([str(msg.uuid) for msg in getAllMessages(request.user.userprofile.uuid, 'readed')], safe=False)

def api_getUnreadedMessages(request):
	if not request.user.is_authenticated():
		return HttpResponseForbidden()

	return JsonResponse([str(msg.uuid) for msg in getAllMessages(request.user.userprofile.uuid, 'unreaded')], safe=False)

def api_getWait(request):
	if not request.user.is_authenticated():
		return HttpResponseForbidden()

	for host in settings.OTHER_HOSTS:
		if not settings.QUEUE[host['id']].empty():
			return HttpResponseBadRequest()
		if settings.SENDER[host['id']].sending:
			return HttpResponseBadRequest()

	if not settings.SET_MANAGER.buffer.empty():
		return HttpResponseBadRequest()

	if not settings.SET_MANAGER.queue.empty():
		return HttpResponseBadRequest()

	return HttpResponse(status=200)