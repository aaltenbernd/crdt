from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

from .models import AddMessage, DeleteMessage, AddFolder, DeleteFolder
from .forms import AddMessageForm, AddFolderForm, LoginForm, RegisterForm, ChangeFolderForm

from django.conf import settings

from .operation import *

def index(request):
    return redirect('show_messages', 'inbox')

def send_message(request):
    if not request.user.is_authenticated():
        return redirect('login')

    form = AddMessageForm()

    if request.method == 'POST':

        form = AddMessageForm(request.POST)

        if form.is_valid():
            text = request.POST.get('text')
            reader_id = request.POST.get('reader')
            reader = User.objects.get(id=reader_id)
            reader_uuid = reader.userprofile.uuid
            author = request.user.username
            author_uuid = request.user.userprofile.uuid

            if reader is None:
                return redirect('index')

            addMessage(text, author, author_uuid, reader, reader_uuid)

            return redirect('index')

    data = {'form': form}

    return redirect('index')

def add_folder(request, active_folder_id):
    if not request.user.is_authenticated():
        return redirect('login')

    if request.method == 'POST':
        form = AddFolderForm(request.POST)

        if form.is_valid():
            title = request.POST.get('title')

            addFolder(title, request.user.userprofile.uuid)

            return redirect('show_messages', active_folder_id)

    return redirect('show_messages', active_folder_id)

def show_messages(request, active_folder_id):
    if not request.user.is_authenticated():
        return redirect('login')

    if active_folder_id == 'inbox':
        active_folder = 'inbox'
    elif active_folder_id == 'outbox':
        active_folder = 'outbox'
    else:
        active_folder = AddFolder.objects.get(uuid=active_folder_id)

    add_folder_form = AddFolderForm()
    add_message_form = AddMessageForm()    

    messages = getAllMessages(request.user.userprofile.uuid, active_folder_id=active_folder_id)

    messages = messages.order_by("-date")

    # get all folder
    folders = getAllFolders(request.user.userprofile.uuid)

    change_folder_form = ChangeFolderForm(active_folder_id=active_folder_id, folders=folders)

    data = {'add_message_form': add_message_form,
            'add_folder_form': add_folder_form, 
            'change_folder_form': change_folder_form,
            'messages': messages, 
            'folders': folders, 
            'other_hosts': settings.OTHER_HOSTS, 
            'running_host': settings.RUNNING_HOST['id'], 
            'active_folder': active_folder, 
            'user': request.user,
            }

    return render(request, 'messages.html', data)

def change_folder(request, active_folder_id, message_id):
    if not request.user.is_authenticated():
        return redirect('login')

    if request.method == 'POST':

        folders = getAllFolders(request.user.userprofile.uuid)

        form = ChangeFolderForm(request.POST, active_folder_id=active_folder_id, folders=folders)

        if form.is_valid():
            folder_choice = request.POST.get('folder_choice')

            changeFolder(message_id, folder_choice)

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

            createUser(username, password, False, False)

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

    deleteMessage(message_id) 

    return redirect('show_messages', active_folder_id)

def delete_folder(request, active_folder_id):
    if not request.user.is_authenticated():
        return redirect('login')

    deleteFolder(active_folder_id)

    return redirect('show_messages', 'inbox')

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

        if operation == 'add':
            add_message = AddMessage(**data)
            add_message.inbox = eval(data['inbox'])
            add_message.save()
            print add_message.inbox
        if operation == 'delete':
            delete_message = DeleteMessage(**data)
            delete_message.save()
        if operation == 'add_folder':
            add_folder = AddFolder(**data)
            add_folder.save()
        if operation == 'delete_folder':
            delete_folder = DeleteFolder(**data)
            delete_folder.save()
        if operation == 'add_user':
            uuid = data.pop('uuid')
            user = User.objects.create_user(**data)
            profile = UserProfile.objects.create(user=user, uuid=uuid)
            user.userprofile = profile

        return redirect('index')
    else:   
        return redirect('index')