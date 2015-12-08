from django.shortcuts import render, redirect
from django.utils import timezone
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import Node, OutgoingOperation, Message
from .forms import MessageForm, LoginForm
import ast

# POST REQUEST : 
#   1. get form input
#   2. check form
#   3. create new number with given content in form
#   4. call broadcast with "add" operation and number title
# ELSE : order numbers by date and create form
def index(request):
    if not request.user.is_authenticated():
        return redirect('login')

    if request.method == 'POST':

        form = MessageForm(request.POST)

        if form.is_valid():
            text = request.POST.get('text')
            message_id = request.user.userprofile.counter

            message = Message.objects.create(text=text, message_id=message_id)

            user = request.user

            user.userprofile.increment()
            user.userprofile.save()

            broadcast('increment', user.username, {})

            data = {}
            data['message_id'] = message.message_id
            data['message_author'] = message.author
            data['message_text'] = message.text
            data['message_date'] = str(message.date)

            broadcast('add', user.username, data)

    form = MessageForm()
        
    messages = Message.objects.order_by('-date')
        
    return render(request, 'index.html', {'messages': messages, 'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']

            login_user = User.objects.get(username=username)

            user = authenticate(username=username, password=password)

            login(request,user)

            return redirect('index')
       
    form = LoginForm() 
    
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('index')

# delete number with given id
# call broadcast with "delete" operation and number title
def delete(request):
    message_id = request.GET.get('id', '')

    try:
        message = Message.objects.filter(id=message_id)[0]
    except(IndexError, ValueError):
        return redirect('index')

    #broadcast('delete', number.title)

    message.delete()    

    return redirect('index')

# delete all numbers saved one the currend host (not distributed)
def delete_all(request):
    for message in Message.objects.all():
        message.delete()

    return redirect('index')

# creates for all nodes in the cluster a new OutgointOperation with a given title and operation
# NOTE : what happens when server crashes while creating open operation
def broadcast(operation, username, data):
    data['operation'] = operation
    data['username'] = username
    for node in Node.objects.all():
        op = OutgoingOperation()
        op.data = str(data)
        op.save()
        node.open_ops.add(op)
        node.save()