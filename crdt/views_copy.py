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


# index page and add operation
# create new message
# get user 
# increment counter -> call broadcast -> save outgoing operation
# send message -> call broadcast -> save outgoing operation 
def index(request):
   return render(request, 'index.html', {})

def show_messages(request):
   return render(request, 'index.html', {})

# login for user session
def login_view(request):
    return render(request, 'index.html', {})

# logout for user session
def logout_view(request):
    logout(request)
    return redirect('index')

# delete operation 
# pick message
# call broadcast -> save outgoing operations
# delete it
def delete(request):
    return render(request, 'index.html', {})

# just for cleaning up (DEBUG)
def delete_all(request):
    return render(request, 'index.html', {})

# handle operations send by send_thread on other hosts
# save incoming operation
def receive(request):
    return render(request, 'index.html', {})

# sending thread
def send_thread(host):
    return render(request, 'index.html', {})
