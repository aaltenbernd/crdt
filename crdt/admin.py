from django.contrib import admin
from .models import UserProfile, AddMessage, DeleteMessage

admin.site.register(UserProfile)
admin.site.register(AddMessage)
admin.site.register(DeleteMessage)