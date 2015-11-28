from django.shortcuts import render, redirect
from .models import Number
from django.views.decorators.csrf import csrf_exempt
import requests
from django.http import HttpResponse

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

		number.save()
		
		return redirect('index')
	
	return redirect('index')

def send(op, number_title):
	r = requests.post("http://127.0.0.1:8000/receive/", data = {'op' : op, 'title' : number_title})
