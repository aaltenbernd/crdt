from django.core.management.base import BaseCommand

from crdt.models import Node
from crdt.connect import send_thread, receive_thread

import thread

class Command(BaseCommand):
	
	def handle(self, *args, **options):

		for node in Node.objects.all():
			print 'Starting thread - handling this host: ' + str(node)
			thread.start_new_thread(send_thread, (node, ))

		print 'Starting thread - handling incoming Operations'
		thread.start_new_thread(receive_thread, ( ))

		while True:
			pass