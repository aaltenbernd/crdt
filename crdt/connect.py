from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from .models import Node, IncomingOperation, Message
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.template.context_processors import csrf

import requests
import thread
import Queue
import time

# POST REQUEST : 
#	1. get content operation name and number title
#	2. save incoming operation
# ELSE : do nothing
#@csrf_exempt
def receive(request):
	if request.method == 'POST':
		data = dict(request.POST.iterlists())

		op = IncomingOperation()
		op.data = str(data)
		op.save()	

		return redirect('index')
	else:	
		return redirect('index')

# receiver thread handling incoming operations
def receive_thread():
	# initial queue
	queue = Queue.Queue()

	# running as long as parent process is running
	while True:
		# put all incoming operations to queue
		for open_op in IncomingOperation.objects.all():
			queue.put(open_op)

		# work of the queue
		while queue.empty() == False:
			op = queue.get()
			print "Incoming: " + str(op)

			data = eval(op.data)

			# get number by given name
			# check which operation and execute operation
			# delete operation so it's only executed one time
			try:
				user = User.objects.get(username=data['username'][0])

				if data['operation'][0] == 'increment':
					user.userprofile.increment()
					user.userprofile.save()
				elif data['operation'][0] == 'add':
					message = Message.objects.filter(message_id=data['message_id'])
					if message is not None:
						message.message_id = message.message_id + 1
						message.save()

					Message.objects.create(
						message_id = data['message_id'][0],
						author = data['message_author'][0],
						text = data['message_text'][0],
						date = data['message_date'][0]
					) 
				op.delete()

			# exception occurs if number don't exist
			# check if operation is add 
			# else try again later
			except ObjectDoesNotExist:
				print 'user dont exist'
				time.sleep(2)
				pass

# sender thread handling one host
# sends all open operations to the host
def send_thread(node):
	# initial queue
	queue = Queue.Queue()

	# run as long as parent process is running
	while True:
		# put all open operations to the queue
		for open_op in node.open_ops.all():
			queue.put(open_op)

		# work off the queue
		while queue.empty() == False:
			op = queue.get()
		

			# sends http post request to given host
			# http://localHost:PORT/receive/ is linked in crdt/urls.py to receive method in connect.py
			# request content is operation name and number title
			# receiver can assign operation to number by given title (but title is not unique right now)
			# if no error occurs, delete operation 
			# else sleep for a while and try again
			
			

			print "Outgoing: " + str(op)
			try:
				URL = str(node) + "/receive/"

				client = requests.session()
				client.get(URL)
				csrftoken = client.cookies['csrftoken']
			
				data = eval(str(op.data))
				data['csrfmiddlewaretoken'] = csrftoken
				cookies = dict(client.cookies)

				r = requests.post(URL, data = data, timeout=5, cookies=cookies)
				op.delete()
			except requests.exceptions.RequestException:
				time.sleep(2)
				print 'fail... trying again'