from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core import serializers

from .models import *

from django.conf import settings

@csrf_exempt
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

@csrf_exempt
def api_addMessage(request):
	if not request.user.is_authenticated():
		return JsonResponse(dict(error=True, message="User is not authenticated."))

	if request.method == 'POST':
		text = request.POST.get('text')
		username = request.POST.get('reader')
		reader = User.objects.get(username=username)

		if reader is None:
			return JsonResponse(dict(error=True, message="User don't exist."))

		print settings.RUNNING_HOST['id']

		message = AddMessage.objects.create(
			text=text,
			reader=reader.username,
			host_id=settings.RUNNING_HOST['id'],
			color=settings.RUNNING_HOST['color'],
			folder_id=None,
			author=request.user.username)

		user = request.user

		user.userprofile.increment()
		user.userprofile.save()

		for host in settings.OTHER_HOSTS:
			settings.QUEUE[host['id']].put({'operation' : 'increment', 'username' : user.username})
			settings.QUEUE[host['id']].put(message.to_dict(user.username, 'add'))

		return JsonResponse(dict(error=False, message="Added message.", uuid=message.uuid))

	return JsonResponse(dict(error=True, message="No post request."))

@csrf_exempt
def api_deleteMessage(request, message_id):
	if not request.user.is_authenticated():
		return JsonResponse(dict(error=True, message="User is not authenticated."))

	add_message = AddMessage.objects.get(uuid=message_id)

	if add_message is None:
		return JsonResponse(dict(error=True, message="Message don't exist."))

	delete_message = DeleteMessage.objects.create(uuid=add_message.uuid, host_id=add_message.host_id)

	for host in settings.OTHER_HOSTS:
		settings.QUEUE[host['id']].put(delete_message.to_dict(request.user.username, 'delete'))

	return JsonResponse(dict(error=False, message="Deleted message.", uuid=delete_message.uuid))

@csrf_exempt
def api_getCurrentState(request):
	if not request.user.is_authenticated():
		return JsonResponse(dict(error=True, message="User is not authenticated."))

	messages = AddMessage.objects.all()
	for delete_message in DeleteMessage.objects.all():
		messages = messages.exclude(uuid=delete_message.uuid)

	return JsonResponse(dict(
		error=False, 
		add_messages_count=AddMessage.objects.all().count(), 
		delete_messages_count=DeleteMessage.objects.all().count(), 
		messages_count=messages.count()))

@csrf_exempt
def api_getQueue(request):
	if not request.user.is_authenticated():
		return JsonResponse(dict(error=True, message="User is not authenticated."))

	response_dict = {}
	for host in settings.OTHER_HOSTS:
		response_dict[host['id']] = settings.QUEUE[host['id']].qsize()

	print response_dict

	return JsonResponse(response_dict)