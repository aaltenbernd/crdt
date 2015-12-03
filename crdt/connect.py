from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from .models import Number, Node

import requests
import thread
import Queue

@csrf_exempt
def receive(request):
	if request.method == 'POST':
		thread.start_new_thread(receive_thread, (request.POST.get('op', None), request.POST.get('title', None)))
		return redirect('index')

	else:	
		return redirect('index')

def receive_thread(op, title):
	try:
		number = Number.objects.filter(title=title)[0]
	except:
		if op == 'add':
			number = Number()
			number.title = title
			number.save()
		return

	if op == 'increment':
		number.increment()
	elif op == 'decrement':
		number.decrement()
		
	if op == 'delete':
		number.delete()
	else:
		number.save()

def send(node):
	queue = Queue.Queue()

	while True:	
		for open_op in node.open_ops.all():
			queue.put(open_op)

		while queue.empty() == False:
			op = queue.get()
			try:
				r = requests.post(str(node) + "/receive/", data = {'op' : op.operation, 'title' : op.num})
				op.delete()
			except(requests.ConnectionError):
				print 'ConnectionError'