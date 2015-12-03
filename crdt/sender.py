from .models import Node

import threading
import Queue

inbox = Queue.Queue()

class Sender(threading.Thread):

	queue = Queue.Queue()
	node = None

	def __init__(self, Node):
		self.node = Node
		print str(self.node)

	def __str__(self):
		print "Thread for : " + str(self.node)

	def run(self):
		while True:
			operation = self.queue.get()
			print operation