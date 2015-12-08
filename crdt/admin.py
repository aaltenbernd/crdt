from django.contrib import admin
from .models import UserProfile, IncomingOperation, OutgoingOperation

admin.site.register(UserProfile)
admin.site.register(IncomingOperation)
admin.site.register(OutgoingOperation)