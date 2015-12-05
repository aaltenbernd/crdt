from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from .models import Number, Node, IncomingOperation

import requests
import thread
import Queue
import time

@csrf_exempt
def receive(request):
	if request.method == 'POST':
		operation = request.POST.get('op', None)
		num = request.POST.get('title', None)

		if not Number.objects.filter(title=num) and operation == 'delete':
			print "Number don't exist..."
			return HttpResponse(content="", status=500)
		else:
			incoming_op = IncomingOperation.objects.create(operation=operation, num=num)
			return HttpResponse(content="", status=200)
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

				if op.operation == 'increment':
					number.increment()
				elif op.operation == 'decrement':
					number.decrement()
		
				if op.operation == 'delete':
					number.delete()
				else:	
					number.save()

				op.delete()
			except:
				if op.operation == 'add':
					number = Number()
					number.title = op.num
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
				r = requests.post(str(node) + "/receive/", data = {'op' : op.operation, 'title' : op.num}, timeout=5)
				if r.status_code == 200:
					op.delete()
			except requests.exceptions.RequestException as e:
				print e
				time.sleep(2)
				print 'fail... trying again'