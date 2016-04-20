import uuid
import json

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from .forms import *
from .operation import *

def index(request):
    return redirect('show_messages', 'inbox', 'unreaded', '0:100')

def send_message(request, active_folder_id, mark):
    if not request.user.is_authenticated():
        return redirect('login')

    form = AddMessageForm()

    if request.method == 'POST':

        form = AddMessageForm(request.POST)

        if form.is_valid():
            text = request.POST.get('text')
            reader = request.POST.get('reader')
            reader_user = User.objects.get(username=reader)
            reader_uuid = reader_user.userprofile.uuid
            author_uuid = request.user.userprofile.uuid

            addMessage(request.user.userprofile.uuid, text, author_uuid, reader_uuid)

            data = procede_data(request, active_folder_id, mark, '0:100')
            return render(request, 'messages.html', data)

    data = procede_data(request, active_folder_id, mark, '0:100')
    data['add_message_form'] = form

    return render(request, 'messages.html', data)

def add_folder(request, active_folder_id, mark):
    if not request.user.is_authenticated():
        return redirect('login')

    if request.method == 'POST':
        form = AddFolderForm(request.POST)

        if form.is_valid():
            title = request.POST.get('title')

            addFolder(request.user.userprofile.uuid, title)

            data = procede_data(request, active_folder_id, mark, '0:100')
            return render(request, 'messages.html', data)

    data = procede_data(request, active_folder_id, mark, '0:100')
    data['add_folder_form'] = form
    return render(request, 'messages.html', data)

def mark(request, message_id, active_folder_id, mark):
    if not request.user.is_authenticated():
        return redirect('login')

    if mark == 'readed':
        mark_unreaded(request.user.userprofile.uuid, message_id)
    if mark == 'unreaded':
        mark_readed(request.user.userprofile.uuid, message_id)

    return redirect('show_messages', active_folder_id, mark, '0:100')

def set_pagination(request, active_folder_id, mark):
    if not request.user.is_authenticated():
        return redirect('login')

    if request.method == 'POST':

        if active_folder_id == 'inbox':
            messages = getAllInboxMessages(request.user.userprofile.uuid, mark)
        elif active_folder_id == 'outbox':
            messages = getAllOutboxMessages(request.user.userprofile.uuid, mark)
        else:
            messages = getAllMessagesInFolder(request.user.userprofile.uuid, active_folder_id, mark)

        form = PaginationForm(request.POST, len_messages=len(messages))

        if form.is_valid():
            msg_slice = request.POST.get('pagination')

            data = procede_data(request, active_folder_id, mark, msg_slice)
            data['pagination_form'] = form
            return render(request, 'messages.html', data)

    return redirect('show_messages', active_folder_id, mark, '0:100')


def procede_data(request, active_folder_id, mark, msg_slice):
    if active_folder_id != 'inbox' and active_folder_id != 'outbox':
        active_folder_id = uuid.UUID(active_folder_id)

    folders = getAllFolders(request.user.userprofile.uuid)

    if active_folder_id == 'inbox':
        messages = getAllInboxMessages(request.user.userprofile.uuid, mark)
    elif active_folder_id == 'outbox':
        messages = getAllOutboxMessages(request.user.userprofile.uuid, mark)
    else:
        messages = getAllMessagesInFolder(request.user.userprofile.uuid, active_folder_id, mark)

    folders = sorted(folders, key=lambda folder: folder.title)
    messages = sorted(messages, key=lambda message: message.date, reverse=True)

    add_folder_form = AddFolderForm()
    
    add_message_form = AddMessageForm()

    change_folder_form = ChangeFolderForm(user_id=request.user.userprofile.uuid)

    len_messages = len(messages)

    pagination_form = PaginationForm(len_messages=len_messages)

    data = {'add_message_form': add_message_form,
            'add_folder_form': add_folder_form, 
            'change_folder_form': change_folder_form,
            'pagination_form': pagination_form,
            'messages': messages, 
            'folders': folders,
            'other_hosts': settings.OTHER_HOSTS, 
            'running_host': settings.RUNNING_HOST['id'], 
            'active_folder_id': active_folder_id,
            'user': request.user,
            'users': User.objects.all(),
            'len_messages': len_messages,
            'len_folders': len(folders),
            'mark': mark,
            'msg_slice': msg_slice
            }

    return data

def show_messages(request, active_folder_id, mark, msg_slice):
    if not request.user.is_authenticated():
        return redirect('login')

    data = procede_data(request, active_folder_id, mark, msg_slice)

    return render(request, 'messages.html', data)

def change_folder(request, active_folder_id, message_id, mark):
    if not request.user.is_authenticated():
        return redirect('login')

    if request.method == 'POST':

        folders = getAllFolders(request.user.userprofile.uuid)

        form = ChangeFolderForm(request.POST, user_id=request.user.userprofile.uuid)

        if form.is_valid():
            folder_choice = request.POST.get('folder_choice')


            if active_folder_id == 'inbox':
                changeFolder(request.user.userprofile.uuid, message_id, 'Inbox', folder_choice)
            else:
                changeFolder(request.user.userprofile.uuid, message_id, active_folder_id, folder_choice)

            data = procede_data(request, active_folder_id, mark, '0:100')
            return render(request, 'messages.html', data)

    data = procede_data(request, active_folder_id, mark, '0:100')
    data['change_folder_form'] = form
    return render(request, 'messages.html', data)

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

def delete(request, active_folder_id, message_id, mark):
    if not request.user.is_authenticated():
        return redirect('login')

    if active_folder_id == 'outbox':
        deleteOutboxMessage(request.user.userprofile.uuid, message_id)
    else:
        deleteMessage(request.user.userprofile.uuid, message_id) 

    return redirect('show_messages', active_folder_id, mark, '0:100')

def delete_folder(request, active_folder_id):
    if not request.user.is_authenticated():
        return redirect('login')

    deleteFolder(request.user.userprofile.uuid, active_folder_id)

    return redirect('show_messages', 'inbox', 'unreaded', '0:100')

def receive(request):
    if request.method == 'POST':
        data_dict = request.POST.dict()        

        #csrftoken = data_dict.pop('csrfmiddlewaretoken')

        data_list = json.loads(data_dict['list'])
        #with open("batch.txt", "a") as f:
        #    f.write("[RECEIVED] " + str(len(data_list)) + " operations.\n")

        for data in data_list:
            print "[RECEIVED] %s" % data['operation']
            
            if data['operation'] == 'flatten':

                settings.FLAT_MANAGER.queue.put(data)
            elif data['operation'] == 'add_user':
                try:
                    user = UserProfile.objects.get(uuid=uuid.UUID(data['uuid']))
                except ObjectDoesNotExist:
                    user = User.objects.create_user(username=data['username'], password=data['password'])
                    profile = UserProfile.objects.create(user=user, uuid=data['uuid'], password=data['password'])
                    user.userprofile = profile
                    user.save()
            else:
                settings.SET_MANAGER.add(data, False)

        return redirect('index')
    else:   
        return redirect('index')

def toQueue(data):
    for host in settings.OTHER_HOSTS:
        settings.SENDER[host['id']].queue.put(dict(**data))