from django.contrib import admin
from .models import UserProfile, AddMessage, AddFolder, DeleteMessage

admin.site.register(UserProfile)
admin.site.register(AddMessage)
admin.site.register(AddFolder)
admin.site.register(DeleteMessage)