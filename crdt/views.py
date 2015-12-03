from django.shortcuts import render, redirect
from .models import Number, Node, Operation
from .forms import NumberForm
from .sender import Sender
from django.utils import timezone
from django.utils.html import escape

def index(request):
    if request.method == 'POST':

        form = NumberForm(request.POST)

        if form.is_valid():
            title = escape(request.POST.get('title'))

            Number.objects.create(title=title)

            #send('add', title)

            return redirect('index')

    else:
        form = NumberForm()
        
    numbers = Number.objects.order_by('-date')
        
    return render(request, 'index.html', {'numbers': numbers, 'form': form})

def increment(request):
    number_id = request.GET.get('id', '')

    try:
        number = Number.objects.filter(id=number_id)[0]
    except(IndexError, ValueError):
        return redirect('index')

    number.increment()

    number.save()

    op = Operation.objects.create(operation='increment', num=number)

    for node in Node.objects.all():
        node.open_ops.add(op)
        node.save()

    # send('increment', number.title);

    return redirect('index')

def decrement(request):
    number_id = request.GET.get('id', '')

    try:
        number = Number.objects.filter(id=number_id)[0]
    except(IndexError, ValueError):
        return redirect('index')

    number.decrement()

    number.save()

    

    # send('decrement', number.title)

    return redirect('index')

def delete(request):
    number_id = request.GET.get('id', '')

    try:
        number = Number.objects.filter(id=number_id)[0]
    except(IndexError, ValueError):
        return redirect('index')

    number.delete()

    #send('delete', number.title)

    return redirect('index')