import json

from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from .models import *

def receive(request):
    """
    Receives a list of operations sent by other hosts.
    Depending on the operation:
        - add_user: creating new user
        - flatten: passing to flat manager
        - other: passing to set manager
    """

    if request.method == 'POST':
        data_dict = request.POST.dict()        

        data_list = json.loads(data_dict['list'])

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