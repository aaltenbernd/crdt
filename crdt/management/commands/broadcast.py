from django.core.management.base import BaseCommand

from crdt.models import Node
from crdt.connect import send_thread, receive_thread

import thread

class Command(BaseCommand):
	
	def handle(self, *args, **options):

		# start one thread for each node of the cluster
		# each thread sends operations to one node of the cluster
		for node in Node.objects.filter(n_self=False):
			print 'Starting thread - handling this host: ' + str(node)
			thread.start_new_thread(send_thread, (node, ))

		# start one thread for receiving operations 
		print 'Starting thread - handling incoming operations'
		thread.start_new_thread(receive_thread, ( ))

		# run as long as there is no KeyboardInterrupt [ctrl + c]
		while True:
			pass