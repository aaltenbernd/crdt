from django.shortcuts import render, redirect
from django.utils import timezone
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.forms import model_to_dict

from .models import Host, AddMessage, DeleteMessage
from .forms import AddMessageForm, LoginForm

import Queue
import thread
import time
import requests

# filter running host and other hosts
running_host = Host.objects.filter(host_self=True)[0]
other_hosts = Host.objects.filter(host_self=False)

# init queues
queue = {}
for host in other_hosts:
    queue[host.host_id] = Queue.Queue()

# index page and add operation
# create new message
# get user 
# increment counter -> call broadcast -> save outgoing operation
# send message -> call broadcast -> save outgoing operation 
def index(request):
    if not request.user.is_authenticated():
        return redirect('login')

    if request.method == 'POST':

        form = AddMessageForm(request.POST)

        if form.is_valid():
            text = request.POST.get('text')

            message = AddMessage.objects.create(text=text, host_id=running_host.host_id)

            user = request.user

            user.userprofile.increment()
            user.userprofile.save()

            for host in other_hosts:
                queue[host.host_id].put({'operation' : 'increment', 'username' : user.username})
                queue[host.host_id].put(message.to_dict(user.username, 'add'))

            return redirect('index')

    form = AddMessageForm()
        
    delete_messages = DeleteMessage.objects.all()

    messages = AddMessage.objects.all()
    for delete_message in DeleteMessage.objects.all():
        messages = messages.exclude(uuid=delete_message.uuid)

    return render(request, 'index.html', {'messages': messages, 'form': form})

# login for user session
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']

            login_user = User.objects.get(username=username)

            user = authenticate(username=username, password=password)

            login(request,user)

            form = LoginForm() 

            return redirect('index')
        else:
            return render(request, 'login.html', {'form': form})
       
    form = LoginForm() 
    
    return render(request, 'login.html', {'form': form})

# logout for user session
def logout_view(request):
    logout(request)
    return redirect('index')

# delete operation 
# pick message
# call broadcast -> save outgoing operations
# delete it
def delete(request):
    if not request.user.is_authenticated():
        return redirect('login')
    
    uuid = request.GET.get('id', '')

    try:
        add_message = AddMessage.objects.filter(uuid=uuid)[0]
    except(IndexError, ValueError):
        return redirect('index')

    delete_message = DeleteMessage.objects.create(uuid=add_message.uuid, host_id=add_message.host_id)

    for host in other_hosts:
        queue[host.host_id].put(delete_message.to_dict(request.user.username, 'delete'))   

    return redirect('index')

# just for cleaning up (DEBUG)
def delete_all(request):
    for message in AddMessage.objects.all():
        message.delete()

    for message in DeleteMessage.objects.all():
        message.delete()

    return redirect('index')

# handle operations send by send_thread on other hosts
# save incoming operation
def receive(request):
    if request.method == 'POST':
        data = request.POST.dict()

        print "\033[91m[RECEIVED] " + data['operation']

        csrftoken = data.pop('csrfmiddlewaretoken')
        operation = data.pop('operation')
        username = data.pop('username')

        user = User.objects.get(username=username)

        if operation == 'increment':
            user.userprofile.increment()
            user.userprofile.save()
        if operation == 'add':
            add_message = AddMessage(**data)
            add_message.save()
        if operation == 'delete':
            delete_message = DeleteMessage(**data)
            delete_message.save()

        return redirect('index')
    else:   
        return redirect('index')

# sending thread
def send_thread(host):
    while True:
        if queue[host.host_id].empty():
            time.sleep(1)
        else:
            data = queue[host.host_id].get()

            print "\033[91m[THREAD " + str(host.host_id) + "] " + data['operation'] + " to " + str(host)

            try:
                # set up csrftoken, because django needs it
                URL = "http://" + str(host) + "/receive/"

                client = requests.session()
                client.get(URL)
                csrftoken = client.cookies['csrftoken']

                data['csrfmiddlewaretoken'] = csrftoken
                cookies = dict(client.cookies)

                # send post request and delete operations
                r = requests.post(URL, data = data, timeout=5, cookies=cookies)

            except requests.exceptions.RequestException:
                time.sleep(2)
                print 'fail... trying again'

for host in other_hosts:
    thread.start_new_thread(send_thread, (host, ))