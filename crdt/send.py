from django.core.management.base import BaseCommand, CommandError
from crdt.models import Node

import thread

def send(node):
	node = Node.objects.filter(id=node_id)

	while True:
		op = node.queue.get()

		try:
			print op[0] + " to " + str(node)
			r = requests.post(str(node) + "/receive/", data = {'op' : op, 'title' : number_title})
		except(requests.ConnectionError):
			print 'ConnectionError'

		print 'Running...'

def startSender(BaseCommand):
	def handle(self, *args, **options):
		print 'CHAKA'

#for node in Node.objects.all():
#	thread.start_new_thread(send, node)

#while True:
#	pass