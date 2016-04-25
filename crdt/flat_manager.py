from django.conf import settings
from .send import toQueue
import Queue
import time

class FlatManager():
	def __init__(self):
		self.flat = False
		self.commit = False
		self.ready = False
		self.coordinator = False
		self.timeout = 0

		self.ready_dict = {}
		self.ack_dict = {}
		for host in settings.OTHER_HOSTS:
			self.ready_dict[host['id']] = False
			self.ack_dict[host['id']] = False

		self.queue = Queue.Queue()

	def clear(self):
		self.flat = False
		self.coordinator = False
		self.commit = False
		self.ready = False

		self.timeout = 0

		for host in settings.OTHER_HOSTS:
			self.ready_dict[host['id']] = False
			self.ack_dict[host['id']] = False

	def getFlat(self):
		return self.flat

	def getCommit(self):
		return self.commit

	def prepare(self):
		self.flat = True

		print '[COORDINATOR] PREPARE : CHECK QUEUES'

		for host in settings.OTHER_HOSTS:
			while not settings.SENDER[host['id']].queue.empty() or settings.SENDER[host['id']].isSending():
				print '[COORDINATOR] PREPARE : QUEUE FULL'
				time.sleep(1)
				pass

		print '[COORDINATOR] PREPARE : SENDING PREPARE'

		self.coordinator = True
		toQueue(dict(operation='flatten', query='prepare', host=settings.RUNNING_HOST['id']))

	def coordinate(self, data):
		if data['query'] == 'prepare':
			print '[COORDINATOR] PREPARE : CHECK IDS'

			if settings.RUNNING_HOST['id'] < data['host']:
				print '[COORDINATOR] PREPARE : ID IS HIGHER'
				self.coordinator = False
				self.follow(data)
			else:
				print '[COORDINATOR] PREPARE : ID IS LOWER'

		if data['query'] == 'ready':
			print '[COORDINATOR] READY : CHECK IF ALL READY'

			self.ready_dict[data['host']] = True

			for host in settings.OTHER_HOSTS:
				if not self.ready_dict[host['id']]:
					print '[COORDINATOR] READY : NOT ALL READY'
					break
			else:
				print '[COORDINATOR] READY : ALL READY ; SENDING COMMIT'

				self.commit = True
				toQueue(dict(operation='flatten', query='commit', host=settings.RUNNING_HOST['id']))				

		if data['query'] == 'ack':
			print '[COORDINATOR] ACK : CHECK IF ALL ACKED'

			self.ack_dict[data['host']] = True

			for host in settings.OTHER_HOSTS:
				if not self.ack_dict[host['id']]:
					print '[COORDINATOR] ACK : NOT ALL ACKED'
					break
			else:
				print '[COORDINATOR] ACK : ALL ACKED ; SENDING CLEAR'

				toQueue(dict(operation='flatten', query='clear', host=settings.RUNNING_HOST['id']))
				
				settings.SET_MANAGER.flat()
				self.clear()
				settings.SET_MANAGER.clearBuffer()
				
				print '[COORDINATOR] FINISHED'

	def follow(self, data):
		if data['query'] == 'prepare':
			self.flat = True

			print '[FOLLOW] PREPARE : CHECK QUEUE'

			for host in settings.OTHER_HOSTS:
				while not settings.SENDER[host['id']].queue.empty() or settings.SENDER[host['id']].isSending():
					print '[FOLLOW] PREPARE : QUEUE FULL'
					time.sleep(1)
					pass

			print '[FOLLOW] PREPARE : SENDING READY'

			settings.SENDER[data['host']].queue.put(dict(operation='flatten', query='ready', host=settings.RUNNING_HOST['id']))

		if data['query'] == 'commit':
			print '[FOLLOW] COMMIT + ACKNOWLEDGE'
			
			self.commit = True
			settings.SENDER[data['host']].queue.put(dict(operation='flatten', query='ack', host=settings.RUNNING_HOST['id']))
		
		if data['query'] == 'clear':
			print '[FOLLOW] FLAT + CLEAR'

			settings.SET_MANAGER.flat()
			self.clear()
			settings.SET_MANAGER.clearBuffer()

			print '[FOLLOW] FINISHED'

		if data['query'] == 'abort':
			print '[FOLLOW] ABORT'
			self.clear()

	def run(self):
		while True:
			try:
				if self.queue.empty():
					if settings.SET_MANAGER.getOpCount() >= 1000 and not self.flat:
						self.prepare()
					else:
						time.sleep(1)
				else:
					data = self.queue.get()
					if self.coordinator:
						if self.commit == True and data['query'] == 'prepare':
							self.queue.put(data)
						else:
							self.coordinate(data)
					else:
						self.follow(data)
			except AttributeError:
				time.sleep(1)