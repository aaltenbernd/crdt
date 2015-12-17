from django.shortcuts import render, redirect
from django.utils import timezone
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.forms import model_to_dict

from .models import Node, Message, OutgoingOperation, IncomingOperation
from .forms import MessageForm, LoginForm

# running host
HOST = Node.objects.filter(n_self=True)[0]

# index page and add operation
# create new message
# get user 
# increment counter -> call broadcast -> save outgoing operation
# send message -> call broadcast -> save outgoing operation 
def index(request):
    if not request.user.is_authenticated():
        return redirect('login')

    if request.method == 'POST':

        form = MessageForm(request.POST)

        if form.is_valid():
            text = request.POST.get('text')
            global_id = request.user.userprofile.counter

            message = Message.objects.create(text=text, global_id=global_id, host_id=HOST.n_id)

            user = request.user

            user.userprofile.increment()
            user.userprofile.save()

            broadcast({'operation' : 'increment', 'username' : user.username})

            broadcast(message.to_dict(user.username, 'add'))

            return redirect('index')

    form = MessageForm()
        
    messages = Message.objects.order_by('-date')
        
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
    
    message_id = request.GET.get('id', '')

    try:
        message = Message.objects.filter(id=message_id)[0]
    except(IndexError, ValueError):
        return redirect('index')

    broadcast(message.to_dict(request.user.username, 'delete'))

    message.delete()    

    return redirect('index')

# just for cleaning up (DEBUG)
def delete_all(request):
    for message in Message.objects.all():
        message.delete()

    return redirect('index')

# save outgoing operation for each node
# what happens if django app crashes? 
# some nodes won't receive operation?
# maybe need to save which ops have been saved for which nodes :S
def broadcast(data):
    for node in Node.objects.filter(n_self=False):
        op = OutgoingOperation()
        op.data = str(data)
        op.save()
        node.open_ops.add(op)
        node.save()

# handle operations send by send_thread on other hosts
# save incoming operation
def receive(request):
    if request.method == 'POST':
        data = request.POST.dict()

        op = IncomingOperation()
        op.data = str(data)
        op.save()
        
        return redirect('index')
    else:   
        return redirect('index')