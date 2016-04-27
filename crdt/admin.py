from django.contrib import admin
from .models import *

admin.site.register(AddMessage)
admin.site.register(DeleteMessage)
admin.site.register(OutboxMessage)
admin.site.register(AddFolder)
admin.site.register(DeleteFolder)
admin.site.register(UserProfile)
admin.site.register(ReadMarker)
admin.site.register(UnreadMarker)