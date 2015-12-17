from django.core.management.base import BaseCommand

from crdt.models import IncomingOperation, OutgoingOperation
from crdt.connect import send_thread, receive_thread

import thread

class Command(BaseCommand):
	
	def handle(self, *args, **options):
		for in_op in IncomingOperation.objects.all():
			in_op.delete()
		for out_op in OutgoingOperation.objects.all():
			out_op.delete()