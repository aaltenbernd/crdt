from django.shortcuts import render, redirect
from django.utils import timezone
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.forms import model_to_dict

from .models import AddMessage, DeleteMessage, AddFolder, DeleteFolder
from .forms import AddMessageForm, AddFolderForm, LoginForm

import thread
import time
import requests

from .host import *

# localHost
HOSTNAME = "http://127.0.0.1"

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

            message = AddMessage.objects.create(text=text, host_id=running_host['id'], folder=None)

            user = request.user

            user.userprofile.increment()
            user.userprofile.save()

            for host in other_hosts:
                queue[host['id']].put({'operation' : 'increment', 'username' : user.username})
                queue[host['id']].put(message.to_dict(user.username, 'add'))

            return redirect('index')

    form = AddMessageForm()

    data = {'form': form, 'other_hosts': other_hosts, 'running_host': running_host['id']}

    return render(request, 'index.html', data)

def show_messages(request, active_host):
    if not request.user.is_authenticated():
        return redirect('login')

    if not active_host:
        active_host = running_host['id']

    if request.method == 'POST':
        form = AddFolderForm(request.POST)

        if form.is_valid():
            title = request.POST.get('title')

            folder = AddFolder.objects.create(title=title, host_id=active_host)

            for host in other_hosts:
                queue[host['id']].put(folder.to_dict(request.user.username))

            return redirect('show_messages', active_host)

    form = AddFolderForm()

    # get all messages
    messages = AddMessage.objects.all()
    for delete_message in DeleteMessage.objects.all():
        messages = messages.exclude(uuid=delete_message.uuid)

    messages = messages.filter(host_id=active_host).order_by('-date')

    # get all folder
    folders = AddFolder.objects.all()
    for delete_folder in DeleteFolder.objects.all():
        folders = folders.exclude(uuid=delete_folder.uuid)

    folders = folders.filter(host_id=active_host).order_by('title')

    data = {'form': form, 'messages': messages, 'folders': folders, 'other_hosts': other_hosts, 'running_host': running_host['id'], 'active_host': int(active_host)}

    return render(request, 'messages.html', data)

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

def delete(request, active_host):
    if not request.user.is_authenticated():
        return redirect('login')
    
    uuid = request.GET.get('id', '')

    try:
        add_message = AddMessage.objects.filter(uuid=uuid)[0]
    except(IndexError, ValueError):
        return redirect('index')

    delete_message = DeleteMessage.objects.create(uuid=add_message.uuid, host_id=add_message.host_id)

    for host in other_hosts:
        queue[host['id']].put(delete_message.to_dict(request.user.username, 'delete'))   

    return redirect('show_messages', active_host)

def delete_folder(request, active_host):
    if not request.user.is_authenticated():
        return redirect('login')
    
    uuid = request.GET.get('id', '')

    try:
        add_folder = AddFolder.objects.filter(uuid=uuid)[0]
    except(IndexError, ValueError):
        return redirect('index')

    delete_folder = DeleteFolder.objects.create(uuid=add_folder.uuid, host_id=add_folder.host_id)

    for host in other_hosts:
        queue[host['id']].put(delete_folder.to_dict(request.user.username))   

    return redirect('show_messages', active_host)

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

        print "[RECEIVED] " + data['operation']

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
        if operation == 'add_folder':
            add_folder = AddFolder(**data)
            add_folder.save()
        if operation == 'delete_folder':
            delete_folder = DeleteFolder(**data)
            delete_folder.save()

        return redirect('index')
    else:   
        return redirect('index')

def get_url(host):
    return "http://" + str(host) + "/receive/"

# sending thread
def send_thread(host):
    while True:
        if queue[host['id']].empty():
            time.sleep(1)
        else:
            data = queue[host['id']].get()

            print "[THREAD " + str(host['id']) + "] " + data['operation'] + " to " + str(host['port'])

            while True:
                try:
                    # set up csrftoken, because django needs it
                    URL = HOSTNAME + ":" + str(host['port']) + "/receive/"

                    client = requests.session()
                    client.get(URL)
                    csrftoken = client.cookies['csrftoken']

                    data['csrfmiddlewaretoken'] = csrftoken
                    cookies = dict(client.cookies)

                    # send post request and delete operations
                    r = requests.post(URL, data = data, timeout=5, cookies=cookies)
                    break
                except requests.exceptions.RequestException:
                    time.sleep(2)
                    print "[THREAD " + str(host['id']) + "] Can't reach host " + str(host['port'])
                    continue

for host in other_hosts:
    thread.start_new_thread(send_thread, (host, ))