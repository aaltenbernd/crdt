from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from .models import Number, Node, IncomingOperation

import requests
import thread
import Queue
import time

# POST REQUEST : 
#	1. get content operation name and number title
#	2. save incoming operation
# ELSE : do nothing
@csrf_exempt
def receive(request):
	if request.method == 'POST':
		operation = request.POST.get('op', None)
		num = request.POST.get('title', None)

		incoming_op = IncomingOperation.objects.create(operation=operation, num=num)

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

			# get number by given name
			# check which operation and execute operation
			# delete operation so it's only executed one time
			try:
				number = Number.objects.filter(title=op.num)[0]

				if op.operation == 'increment':
					number.increment()
				elif op.operation == 'decrement':
					number.decrement()
		
				if op.operation == 'delete':
					number.delete()
				else:	
					number.save()

				op.delete()
			# exception occurs if number don't exist
			# check if operation is add 
			# else try again later
			except:
				if op.operation == 'add':
					number = Number()
					number.title = op.num
					number.save()
					op.delete()

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
			print "Outgoing: " + str(op)

			# sends http post request to given host
			# http://localHost:PORT/receive/ is linked in crdt/urls.py to receive method in connect.py
			# request content is operation name and number title
			# receiver can assign operation to number by given title (but title is not unique right now)
			# if no error occurs, delete operation 
			# else sleep for a while and try again
			try:
				r = requests.post(str(node) + "/receive/", data = {'op' : op.operation, 'title' : op.num}, timeout=5)
				op.delete()
			except requests.exceptions.RequestException:
				time.sleep(2)
				print 'fail... trying again'