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
	# in case a add comes in with same message
	goint_to_delete = []

	# running as long as parent process is running
	while True:
		# put all incoming operations to queue
		for open_op in IncomingOperation.objects.all():
			queue.put(open_op)

		# work of the queue
		while queue.empty() == False:
			op = queue.get()

			# get message dict
			data = eval(op.data)

			# get csrftoken, operation, username token of the message dict
			try:
				csrftoken = data.pop('csrfmiddlewaretoken')
				operation = data.pop('operation')
				username = data.pop('username')
			except:
				print 'csrftoken, operation or username error'
				op.delete()
				continue

			print "Incoming: " + operation

			try:
				# get user
				user = User.objects.get(username=username)

				# check which operation
				if operation == 'increment':
					# increment distributed counter
					user.userprofile.increment()
					user.userprofile.save()
				elif operation == 'add':
					# check if message is already in "going_to_delete" list
					# check by global_id and host_id => unique
					delete_op_exist = False
					for message in goint_to_delete:
						if message['global_id'] == data['global_id'] and message['host_id'] == data['host_id']:
							delete_op_exist = True

					# add message
					if delete_op_exist == False:
						message = Message(**data)
						message.save()
						pass
					else:
						print 'delete op already exist'	
				elif operation == 'delete':
					try:
						# get message and delete it
						message = Message.objects.get(**data)
						message.delete()
					except ObjectDoesNotExist:
						print 'message dont exist'
						print 'put op to delete list'
						# put message to "going_to_delete" list in case message don't exist
						goint_to_delete.append(data)
				op.delete()

			except ObjectDoesNotExist:
				# maybe user don't exist right now
				# take another operation and try again later
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
				# get message dict
				data = eval(str(op.data))

				print "Outgoing: " + str(data['operation'])

				# set up csrftoken, because django needs it
				URL = str(node) + "/receive/"

				client = requests.session()
				client.get(URL)
				csrftoken = client.cookies['csrftoken']

				data['csrfmiddlewaretoken'] = csrftoken
				cookies = dict(client.cookies)

				# send post request and delete operation
				r = requests.post(URL, data = data, timeout=5, cookies=cookies)
				op.delete()
			except requests.exceptions.RequestException:
				time.sleep(2)
				print 'fail... trying again'