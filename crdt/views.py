from django.shortcuts import render, redirect
from .models import Number
from .forms import NumberForm
from django.utils import timezone
from django.utils.html import escape

def index(request):
    if request.method == 'POST':

        form = NumberForm(request.POST)

        if form.is_valid():
            title = escape(request.POST.get('title'))
            Number.objects.create(title=title)
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

    return redirect('index')

def decrement(request):
    number_id = request.GET.get('id', '')

    try:
        number = Number.objects.filter(id=number_id)[0]
    except(IndexError, ValueError):
        return redirect('index')

    number.decrement()

    number.save()

    return redirect('index')

def delete(request):
    number_id = request.GET.get('id', '')

    try:
        number = Number.objects.filter(id=number_id)[0]
    except(IndexError, ValueError):
        return redirect('index')

    number.delete()

    return redirect('index')