from django.shortcuts import render, redirect
from django.utils import timezone
from django.utils.html import escape

from .models import Number, Node, OutgoingOperation
from .forms import NumberForm

# POST REQUEST : 
#   1. get form input
#   2. check form
#   3. create new number with given content in form
#   4. call broadcast with "add" operation and number title
# ELSE : order numbers by date and create form
def index(request):
    if request.method == 'POST':

        form = NumberForm(request.POST)

        if form.is_valid():
            title = escape(request.POST.get('title'))

            Number.objects.create(title=title)

            broadcast('add', title)

            return redirect('index')

    else:
        form = NumberForm()
        
    numbers = Number.objects.order_by('-date')
        
    return render(request, 'index.html', {'numbers': numbers, 'form': form})

# increment number with given id
# call broadcast with "increment" operation and number title
def increment(request):
    number_id = request.GET.get('id', '')

    try:
        number = Number.objects.filter(id=number_id)[0]
    except(IndexError, ValueError):
        return redirect('index')

    number.increment()

    number.save()

    broadcast('increment', number.title)

    return redirect('index')

# decrement number with given id
# call broadcast with "decrement" operation and number title
def decrement(request):
    number_id = request.GET.get('id', '')

    try:
        number = Number.objects.filter(id=number_id)[0]
    except(IndexError, ValueError):
        return redirect('index')

    number.decrement()

    number.save()

    broadcast('decrement', number.title)

    return redirect('index')

# delete number with given id
# call broadcast with "delete" operation and number title
def delete(request):
    number_id = request.GET.get('id', '')

    try:
        number = Number.objects.filter(id=number_id)[0]
    except(IndexError, ValueError):
        return redirect('index')

    broadcast('delete', number.title)

    number.delete()    

    return redirect('index')

# delete all numbers saved one the currend host (not distributed)
def delete_all(request):
    for num in Number.objects.all():
        num.delete()

    return redirect('index')

# creates for all nodes in the cluster a new OutgointOperation with a given title and operation
# NOTE : what happens when server crashes while creating open operation
def broadcast(operation, number_title):
    for node in Node.objects.all():
        op = OutgoingOperation.objects.create(operation=operation, num=number_title)
        node.open_ops.add(op)
        node.save()