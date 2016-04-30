import Queue
import time

from django.conf import settings
from .send import toQueue

class FlatManager():
	"""
	Flat Manager Class.
	Coordinating the flatten process.
	"""

	def __init__(self):
		self.flat = False
		self.commit = False
		self.ready = False
		self.coordinator = False
		self.timeout = 0

		# for collecting answers of the follower
		self.ready_dict = {}
		self.ack_dict = {}

		for host in settings.OTHER_HOSTS:
			self.ready_dict[host['id']] = False
			self.ack_dict[host['id']] = False

		self.queue = Queue.Queue()

	def clear(self):
		"""Resets the flat manager class."""

		self.flat = False
		self.coordinator = False
		self.commit = False
		self.ready = False

		self.timeout = 0

		for host in settings.OTHER_HOSTS:
			self.ready_dict[host['id']] = False
			self.ack_dict[host['id']] = False

	def getFlat(self):
		"""Returning true if the flatten process is initiating."""

		return self.flat

	def getCommit(self):
		"""Returning true if hosts commited on flatten."""

		return self.commit

	def prepare(self):
		"""Iniating the flatten process by sending the prepare message."""

		self.flat = True

		print '[COORDINATOR] PREPARE : CHECK QUEUES'

		for host in settings.OTHER_HOSTS:
			while not settings.SENDER[host['id']].queue.empty() or settings.SENDER[host['id']].isSending():
				print '[COORDINATOR] PREPARE : QUEUE FULL'
				time.sleep(1)
				pass

		print '[COORDINATOR] PREPARE : SENDING PREPARE'

		self.coordinator = True
		toQueue(
			dict(
				operation='flatten',
				query='prepare',
				host=settings.RUNNING_HOST['id']
			)
		)

	def coordinate(self, data):
		"""Coordinating the flatten process."""

		# Getting the prepare message (check ids)
		if data['query'] == 'prepare':
			print '[COORDINATOR] PREPARE : CHECK IDS'

			if settings.RUNNING_HOST['id'] < data['host']:
				print '[COORDINATOR] PREPARE : ID IS HIGHER'
				self.coordinator = False
				self.follow(data)
			else:
				print '[COORDINATOR] PREPARE : ID IS LOWER'

		# Getting the ready message
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
				toQueue(
					dict(
						operation='flatten', 
						query='commit', 
						host=settings.RUNNING_HOST['id']
					)
				)				

		# Getting the ack message
		if data['query'] == 'ack':
			print '[COORDINATOR] ACK : CHECK IF ALL ACKED'

			self.ack_dict[data['host']] = True

			for host in settings.OTHER_HOSTS:
				if not self.ack_dict[host['id']]:
					print '[COORDINATOR] ACK : NOT ALL ACKED'
					break
			else:
				print '[COORDINATOR] ACK : ALL ACKED ; SENDING CLEAR'

				toQueue(
					dict(
						operation='flatten', 
						query='clear', 
						host=settings.RUNNING_HOST['id']
					)
				)
				
				settings.SET_MANAGER.flat()
				self.clear()
				settings.SET_MANAGER.clearBuffer()
				
				print '[COORDINATOR] FINISHED'

	def follow(self, data):
		"""Process to answer the coordinator."""

		# Getting the prepare message
		if data['query'] == 'prepare':
			self.flat = True

			print '[FOLLOW] PREPARE : CHECK QUEUE'

			for host in settings.OTHER_HOSTS:
				while not settings.SENDER[host['id']].queue.empty() or settings.SENDER[host['id']].isSending():
					print '[FOLLOW] PREPARE : QUEUE FULL'
					time.sleep(1)
					pass

			print '[FOLLOW] PREPARE : SENDING READY'

			settings.SENDER[data['host']].queue.put(
				dict(
					operation='flatten',
					query='ready', 
					host=settings.RUNNING_HOST['id']
				)
			)

		# Getting the commit message
		if data['query'] == 'commit':
			print '[FOLLOW] COMMIT + ACKNOWLEDGE'
			
			self.commit = True
			settings.SENDER[data['host']].queue.put(
				dict(
					operation='flatten', 
					query='ack', 
					host=settings.RUNNING_HOST['id']
				)
			)
		
		# Getting the clear message -> do the flatten and reset the flat manager
		if data['query'] == 'clear':
			print '[FOLLOW] FLAT + CLEAR'

			settings.SET_MANAGER.flat()
			self.clear()
			settings.SET_MANAGER.clearBuffer()

			print '[FOLLOW] FINISHED'

		# Getting the abort message -> reset flat manager 
		if data['query'] == 'abort':
			print '[FOLLOW] ABORT'
			self.clear()

	def run(self):
		"""
		Run the flatten thread. 
		Flatten queries are added to queue by receice.py.
		Handling and initiating flatten queries.
		"""

		while True:
			try:
				if self.queue.empty():
					# flat every 1000 operations
					if settings.SET_MANAGER.getOpCount() >= 1000 and not self.flat:
						self.prepare()
					else:
						time.sleep(1)
				else:
					data = self.queue.get()
					if self.coordinator:
						# If commit is true handle prepare messages later
						if self.commit == True and data['query'] == 'prepare':
							self.queue.put(data)
						else:
							self.coordinate(data)
					else:
						self.follow(data)
			except AttributeError:
				time.sleep(1)