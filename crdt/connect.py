from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from .models import Number, Node

import requests
import Queue

@csrf_exempt
def receive(request):
	if request.method == 'POST':
		op = request.POST.get('op', None)
		title = request.POST.get('title', None)

		try:
			number = Number.objects.filter(title=title)[0]
		except:
			if op == 'add':
				number = Number()
				number.title = title
				number.save()
			return redirect('index')

		if op == 'increment':
			number.increment()
		elif op == 'decrement':
			number.decrement()
		
		if op == 'delete':
			number.delete()
		else:
			number.save()
		
		return redirect('index')
	
	return redirect('index')

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