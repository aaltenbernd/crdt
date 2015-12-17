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

# receiver thread handling incoming operations
def receive_thread():
	# initial queue
	queue = Queue.Queue()
	
	# list of messages, goint to delete
	goint_to_delete = []

	# running as long as parent process is running
	while True:
		# put all incoming operations to queue
		for open_op in IncomingOperation.objects.all():
			queue.put(open_op)

		# work of the queue
		while queue.empty() == False:
			op = queue.get()

			data = eval(op.data)

			try:
				csrf = data.pop('csrfmiddlewaretoken')
			except:
				print 'csrftoken error'
				op.delete()
				continue

			try:	
				operation = data.pop('operation')
			except:
				print 'operation error'
				op.delete()
				continue

			try:
				username = data.pop('username')
			except:
				print 'user error'
				op.delete()
				continue

			print "Incoming: " + operation

			try:
				user = User.objects.get(username=username)

				if operation == 'increment':
					user.userprofile.increment()
					user.userprofile.save()
				elif operation == 'add':
					delete_op_exist = False
					for message in goint_to_delete:
						if message['global_id'] == data['global_id'] and message['host_id'] == data['host_id']:
							delete_op_exist = True
					if delete_op_exist == False:
						message = Message(**data)
						message.save()
						pass
					else:
						print 'delete op already exist'	
				elif operation == 'delete':
					try:
						message = Message.objects.get(**data)
						message.delete()
					except ObjectDoesNotExist:
						print 'message dont exist'
						print 'put op to delete list'
						goint_to_delete.append(data)
				op.delete()

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

			try:
				URL = str(node) + "/receive/"

				client = requests.session()
				client.get(URL)
				csrftoken = client.cookies['csrftoken']
			
				data = eval(str(op.data))

				print "Outgoing: " + str(data['operation'])
				data['csrfmiddlewaretoken'] = csrftoken
				cookies = dict(client.cookies)

				r = requests.post(URL, data = data, timeout=5, cookies=cookies)
				op.delete()
			except requests.exceptions.RequestException:
				time.sleep(2)
				print 'fail... trying again: ' + "Outgoing: " + str(data['operation'])