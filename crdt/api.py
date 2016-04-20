import json

from django.http import HttpResponseForbidden, HttpResponseNotFound, HttpResponseBadRequest, HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.conf import settings

from .models import *
from .operation import *

# HttpResponseBadRequest = 400 status code
# HttpResponseForbidden = 403 status code
# HttpResponseNotFound = 404 status code

def api_register(request):
	"""Register procedure with given username and password in the post request."""

	if request.method == 'POST':
		username = request.POST['username']
		password = request.POST['password']
		password_confirm = request.POST['password_confirm']

		if password != password_confirm:
			return HttpResponseBadRequest()

		try:
			createUser(
				username, 
				password
			)

			return HttpResponse(status=200)
		except:
			return HttpResponseBadRequest() 


	return HttpResponseNotFound()

def api_login(request):
	"""Login procedure with given username and password in the post request."""

	if request.method == 'POST':
		username = request.POST.get('username')

		if username is None:
			return HttpResponseBadRequest()

		password = request.POST.get('password')

		if password is None:
			return HttpResponseBadRequest()

		user = authenticate(
			username=username, 
			password=password
		)

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
	"""Logout procedure of the given session in client cookies."""

	logout(request)

	return HttpResponse(status=200)

def api_addMessage(request):
	"""Add message procedure with the given text and reader in the post request."""

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

		time = addMessage(
			request.user.userprofile.uuid,
			text, 
			author_uuid, 
			reader_uuid
		)

		if time is None:
			return HttpResponseBadRequest()
		else:			
			return JsonResponse(dict(time=time))

	return HttpResponseNotFound()

def api_deleteMessage(request):
	"""Delete message procedure with the given uuid in the post request."""

	if not request.user.is_authenticated():
		return HttpResponseForbidden()

	if request.method == 'POST':
		message_id = request.POST.get('message_id')

		time = deleteMessage(
			request.user.userprofile.uuid,
			message_id
		)

		if time is None:
			return HttpResponseBadRequest()
		else:
			return JsonResponse(dict(time=time))

	return HttpResponseNotFound()

def api_addFolder(request):
	"""Add folder procedure with the given titel in the post request."""

	if not request.user.is_authenticated():
		return HttpResponseForbidden()

	if request.method == "POST":

		title = request.POST.get('title')

		time = addFolder(
			request.user.userprofile.uuid,
			title
		)

		if time is None:
			return HttpResponseBadRequest()
		else:
			return JsonResponse(dict(time=time))

	return HttpResponseNotFound()

def api_deleteFolder(request):
	"""Delete folder procedure with the given uuid in the post request."""

	if not request.user.is_authenticated():
		return HttpResponseForbidden()

	if request.method == "POST":
		folder_id = request.POST.get('folder_id')

		time = deleteFolder(
			request.user.userprofile.uuid, 
			folder_id
		)

		if time is None:
			return HttpResponseBadRequest()
		else:
			return JsonResponse(dict(time=time))

	return HttpResponseNotFound()

def api_changeFolder(request):
	"""
	Change folder procedure with the given uuid, 
	old folder and new folder in the post request.
	"""

	if not request.user.is_authenticated():
		return HttpResponseForbidden()

	if request.method == "POST":
		message_id = request.POST.get('message_id')
		folder_choice = request.POST.get('folder_choice')
		old_folder = request.POST.get('old_folder')

		time = changeFolder(
			request.user.userprofile.uuid, 
			message_id, 
			old_folder, 
			folder_choice
		)

		if time is None:
			return HttpResponseBadRequest()
		else:
			return JsonResponse(dict(time=time))

	return HttpResponseNotFound()

def api_mark_readed(request):
	"""Mark read procedure with given uuid in the post request."""

	if not request.user.is_authenticated():
		return HttpResponseForbidden()

	if request.method == "POST":
		message_id = request.POST.get('message_id')

		time = mark_readed(
			request.user.userprofile.uuid, 
			message_id
		)

		return JsonResponse(dict(time=time))

	return HttpResponseNotFound()

def api_mark_unreaded(request):
	"""Mark unread procedure with given uuid in the post request."""

	if not request.user.is_authenticated():
		return HttpResponseForbidden()

	if request.method == "POST":
		message_id = request.POST.get('message_id')

		time = mark_unreaded(
			request.user.userprofile.uuid, 
			message_id
		)

		return JsonResponse(dict(time=time))

	return HttpResponseNotFound()

def api_getState(request):
	"""Returns a dictionary containing the current state."""

	if not request.user.is_authenticated():
		return HttpResponseForbidden()

	state = dict()
	state['inbox'] = [str(msg.uuid) for msg in settings.SET_MANAGER.getInbox()]
	state['outbox'] = [str(msg.uuid) for msg in settings.SET_MANAGER.getOutbox()]
	state['folders'] = [str(fol.uuid) for fol in settings.SET_MANAGER.getFolders()]
	state['all'] = [str(msg.uuid) for msg in getAllMessages(request.user.userprofile.uuid, 'all')]
	state['readed'] = [str(msg.uuid) for msg in getAllMessages(request.user.userprofile.uuid, 'readed')]
	state['unreaded'] = [str(msg.uuid) for msg in getAllMessages(request.user.userprofile.uuid, 'unreaded')]
	for folder_id in state['folders']:
		state[folder_id] = [str(msg.uuid) for msg in settings.SET_MANAGER.getInFolder(str(folder_id))]

	return JsonResponse(state)

def api_getOutbox(request):
	"""Returns a list containing the messages in the outbox."""

	if not request.user.is_authenticated():
		return HttpResponseForbidden()

	return JsonResponse(
		[str(msg.uuid) for msg in settings.SET_MANAGER.getOutbox()], 
		safe=False
	)

def api_getInbox(request):
	"""Returns a list containing the messages in the inbox."""

	if not request.user.is_authenticated():
		return HttpResponseForbidden()

	return JsonResponse(
		[str(msg.uuid) for msg in settings.SET_MANAGER.getInbox()], 
		safe=False
	)

def api_getFolders(request):
	"""Returns a list containing the folders."""

	if not request.user.is_authenticated():
		return HttpResponseForbidden()

	return JsonResponse(
		[str(fol.uuid) for fol in settings.SET_MANAGER.getFolders()], 
		safe=False
	)

def api_getInFolder(request):
	"""Returns a list containing the messages in the given folder."""

	if not request.user.is_authenticated():
		return HttpResponseForbidden()

	if request.method == "POST":
		folder_id = request.POST.get('folder_id')

		return JsonResponse(
			[str(msg.uuid) for msg in settings.SET_MANAGER.getInFolder(str(folder_id))],
			safe=False
		)

	return HttpResponseNotFound()

def api_getAllMessages(request):
	"""Returns a list containing all messages."""

	if not request.user.is_authenticated():
		return HttpResponseForbidden()

	return JsonResponse(
		[str(msg.uuid) for msg in getAllMessages(request.user.userprofile.uuid, 'all')],
		safe=False
	)

def api_getReadedMessages(request):
	"""Returns a list containing read messages."""

	if not request.user.is_authenticated():
		return HttpResponseForbidden()

	return JsonResponse(
		[str(msg.uuid) for msg in getAllMessages(request.user.userprofile.uuid, 'readed')],
		safe=False
	)

def api_getUnreadedMessages(request):
	"""Returns a list containing unread messages."""

	if not request.user.is_authenticated():
		return HttpResponseForbidden()

	return JsonResponse(
		[str(msg.uuid) for msg in getAllMessages(request.user.userprofile.uuid, 'unreaded')],
		safe=False
	)

def api_getWait(request):
	"""
	Returns HTTP OK,
	if host is not distributing or working off any queues/buffers.
	"""

	if not request.user.is_authenticated():
		return HttpResponseForbidden()

	for host in settings.OTHER_HOSTS:
		if not settings.SENDER[host['id']].queue.empty():
			return HttpResponseBadRequest()
		if settings.SENDER[host['id']].sending:
			return HttpResponseBadRequest()

	if not settings.SET_MANAGER.buffer.empty():
		return HttpResponseBadRequest()

	if not settings.SET_MANAGER.queue.empty():
		return HttpResponseBadRequest()

	return HttpResponse(status=200)