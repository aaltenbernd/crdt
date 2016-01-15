from django.contrib import admin
from .models import UserProfile, AddMessage, AddFolder, DeleteFolder, DeleteMessage

admin.site.register(UserProfile)
admin.site.register(AddMessage)
admin.site.register(DeleteMessage)
admin.site.register(AddFolder)
admin.site.register(DeleteFolder)