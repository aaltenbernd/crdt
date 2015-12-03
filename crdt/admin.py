from django.contrib import admin
from .models import Number, Node, IncomingOperation, OutgoingOperation

admin.site.register(Number)
admin.site.register(Node)
admin.site.register(IncomingOperation)
admin.site.register(OutgoingOperation)