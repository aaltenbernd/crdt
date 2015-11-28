from .models import Number
from django.views.decorators.csrf import csrf_exempt
import requests

@csrf_exempt
def receive(request):
	op = request.POST['op']
	title = request.POST['title']
	
	number = Number.objects.filter(title=title)[0]

	if op == 'increment':
		number.increment()
	elif op == 'decrement':
		number.decrement()

	number.save()

def send(op, number_title):
	r = requests.post("http://127.0.0.1:8000/receive", data = {'op' : op, 'title' : number_title})