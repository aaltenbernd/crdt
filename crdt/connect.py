from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from .models import Number, Node, IncomingOperation

import requests
import thread
import Queue

@csrf_exempt
def receive(request):
	if request.method == 'POST':
		operation = request.POST.get('op', None)
		num = request.POST.get('title', None)

		incoming_op = IncomingOperation.objects.create(operation=operation, num=num)

		return redirect('index')
	else:	
		return redirect('index')

def receive_thread():
	queue = Queue.Queue()

	while True:
		for open_op in IncomingOperation.objects.all():
			queue.put(open_op)

		while queue.empty() == False:
			op = queue.get()
			print "Incoming: " + str(op)

			try:
				number = Number.objects.filter(title=op.num)[0]
				if op == 'increment':
					number.increment()
				elif op == 'decrement':
					number.decrement()
		
				if op == 'delete':
					number.delete()
				else:	
					number.save()

				op.delete()
			except:
				if op == 'add':
					number = Number()
					number.title = title
					number.save()
					op.delete()			

def send_thread(node):
	queue = Queue.Queue()

	while True:	
		for open_op in node.open_ops.all():
			queue.put(open_op)

		while queue.empty() == False:
			op = queue.get()
			print "Outgoing: " + str(op)
			try:
				r = requests.post(str(node) + "/receive/", data = {'op' : op.operation, 'title' : op.num})
				op.delete()
			except(requests.ConnectionError):
				print 'ConnectionError'