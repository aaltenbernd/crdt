from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

from .models import AddMessage, DeleteMessage, AddFolder, DeleteFolder, createUser
from .forms import AddMessageForm, AddFolderForm, LoginForm, RegisterForm, ChangeFolderForm

import thread
import time
import requests

from django.conf import settings

# localHost
HOSTNAME = "http://127.0.0.1"

def index(request):
    if not request.user.is_authenticated():
        return redirect('login')

    form = AddMessageForm()

    if request.method == 'POST':

        form = AddMessageForm(request.POST)

        if form.is_valid():
            text = request.POST.get('text')
            reader_id = request.POST.get('reader')
            reader = User.objects.get(id=reader_id)

            message = AddMessage.objects.create(text=text, reader=reader, host_id=settings.RUNNING_HOST['id'], color=settings.RUNNING_HOST['color'], folder_id=None, author=request.user.username)

            user = request.user

            user.userprofile.increment()
            user.userprofile.save()

            for host in settings.OTHER_HOSTS:
                settings.QUEUE[host['id']].put({'operation' : 'increment', 'username' : user.username})
                settings.QUEUE[host['id']].put(message.to_dict(user.username, 'add'))

            return redirect('index')

    data = {'form': form, 'host_color': settings.RUNNING_HOST['color']}

    return render(request, 'index.html', data)

def getAllMessages():
    messages = AddMessage.objects.all()
    for delete_message in DeleteMessage.objects.all():
        messages = messages.exclude(uuid=delete_message.uuid)

    return messages

def getAllFolders():
    folders = AddFolder.objects.all()
    for delete_folder in DeleteFolder.objects.all():
        folders = folders.exclude(uuid=delete_folder.uuid)

    return folders

def add_folder(request, active_folder_id):
    if not request.user.is_authenticated():
        return redirect('login')

    if request.method == 'POST':
        form = AddFolderForm(request.POST)

        if form.is_valid():
            title = request.POST.get('title')

            folder = AddFolder.objects.create(title=title, host_id=settings.RUNNING_HOST['id'], color=settings.RUNNING_HOST['color'])

            for host in settings.OTHER_HOSTS:
                settings.QUEUE[host['id']].put(folder.to_dict(request.user.username))

            return redirect('show_messages', active_folder_id)

    return redirect('show_messages', active_folder_id)

def show_messages(request, active_folder_id):
    if not request.user.is_authenticated():
        return redirect('login')

    if active_folder_id == 'None':
        active_folder = None
    else:
        active_folder = AddFolder.objects.get(uuid=active_folder_id)

    form = AddFolderForm()
    change_folder_form = ChangeFolderForm(active_folder_id=active_folder_id)

    # get all messages in current folder
    messages = getAllMessages()

    messages = messages.order_by('-date')
    if active_folder_id == 'None':
        messages = messages.filter(folder_id=None)
    else:
        messages = messages.filter(folder_id=active_folder_id)

    # get all folder
    folders = getAllFolders()

    folders = folders.order_by('title')

    data = {'form': form, 
            'change_folder_form': change_folder_form,
            'messages': messages, 
            'folders': folders, 
            'other_hosts': settings.OTHER_HOSTS, 
            'running_host': settings.RUNNING_HOST['id'], 
            'active_folder': active_folder, 
            'host_color': settings.RUNNING_HOST['color'],
            }

    return render(request, 'messages.html', data)

def change_folder(request, active_folder_id, message_id):
    if not request.user.is_authenticated():
        return redirect('login')

    if request.method == 'POST':

        form = ChangeFolderForm(request.POST, active_folder_id=active_folder_id)

        if form.is_valid():
            folder_choice = request.POST.get('folder_choice')

            if not folder_choice:
                folder_choice = None
   
            add_message = AddMessage.objects.get(uuid=message_id)

            if add_message is None:
                return redirect('show_messages', active_folder_id)

            print '[Folder id:] ' + str(add_message.folder_id)
            print '[Folder choice:] ' + str(folder_choice)

            if str(add_message.folder_id) == str(folder_choice):
                print '[same folder]'
                return redirect('show_messages', active_folder_id)

            delete_message = DeleteMessage.objects.create(uuid=add_message.uuid, host_id=add_message.host_id)

            new_message = AddMessage.objects.create(text=add_message.text, host_id=add_message.host_id, folder_id=folder_choice, color=add_message.color, date=add_message.date)

            for host in settings.OTHER_HOSTS:
                settings.QUEUE[host['id']].put(delete_message.to_dict(request.user.username, 'delete'))
                settings.QUEUE[host['id']].put(new_message.to_dict(request.user.username, 'add'))

            return redirect('show_messages', active_folder_id)

    return redirect('show_messages', active_folder_id)

def login_view(request):
    form = LoginForm()

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']

            login_user = User.objects.get(username=username)

            user = authenticate(username=username, password=password)

            login(request,user)

            return redirect('index')
        else:
            return render(request, 'login.html', {'form': form})
    
    return render(request, 'login.html', {'form': form})

def register(request):
    form = RegisterForm()

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']

            createUser(username, password)

            return redirect('login')
        else:
            return render(request, 'register.html', {'form': form})

    return render(request, 'register.html', {'form': form})

# logout for user session
def logout_view(request):
    logout(request)
    return redirect('index')

def delete(request, active_folder_id, message_id):
    if not request.user.is_authenticated():
        return redirect('login')

    add_message = AddMessage.objects.get(uuid=message_id)

    if add_message is None:
        return redirect('show_messages', active_folder_id)

    delete_message = DeleteMessage.objects.create(uuid=add_message.uuid, host_id=add_message.host_id)

    for host in settings.OTHER_HOSTS:
        settings.QUEUE[host['id']].put(delete_message.to_dict(request.user.username, 'delete'))   

    return redirect('show_messages', active_folder_id)

def delete_folder(request, active_folder_id):
    if not request.user.is_authenticated():
        return redirect('login')

    add_folder = AddFolder.objects.get(uuid=active_folder_id)

    if add_folder == None:
        return redirect('show_messages', active_folder_id)

    delete_folder = DeleteFolder.objects.create(uuid=add_folder.uuid, host_id=add_folder.host_id)

    for host in settings.OTHER_HOSTS:
        settings.QUEUE[host['id']].put(delete_folder.to_dict(request.user.username))

    messages = getAllMessages()
    messages = messages.filter(folder_id=add_folder.uuid)

    for add_message in messages:
        delete_message = DeleteMessage.objects.create(uuid=add_message.uuid, host_id=add_message.host_id)
        for host in settings.OTHER_HOSTS:
            settings.QUEUE[host['id']].put(delete_message.to_dict(request.user.username, 'delete'))

    return redirect('show_messages', None)

def delete_all(request):
    if not request.user.is_authenticated():
        return redirect('login')

    for message in AddMessage.objects.all():
        message.delete()

    for message in DeleteMessage.objects.all():
        message.delete()

    for folder in AddFolder.objects.all():
        folder.delete()

    for folder in DeleteFolder.objects.all():
        folder.delete()

    request.user.userprofile.counter = 0
    request.user.userprofile.save()

    return redirect('index')

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

def send_thread(host):
    while True:
        if settings.QUEUE[host['id']].empty():
            time.sleep(1)
        else:
            data = settings.QUEUE[host['id']].get()

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

for host in settings.OTHER_HOSTS:
    thread.start_new_thread(send_thread, (host, ))