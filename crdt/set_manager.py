import django
import uuid
import time
import Queue
import requests
import json

django.setup()

from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password, is_password_usable
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from .models import *

HOSTNAME = "http://127.0.0.1"

class SetManager():
	def __init__(self):
		self.add_messages = set(AddMessage.objects.filter(folder_id = None))
		self.delete_messages = set(DeleteMessage.objects.all())
		self.add_folders = set(AddFolder.objects.all())
		self.delete_folders = set(DeleteFolder.objects.all())
		self.outbox_messages = set(OutboxMessage.objects.all())

		self.messages_dict = {}
		self.mark = {}
		for message in self.add_messages:
			self.messages_dict[str(message.uuid)] = message
			self.mark[str(message.uuid)] = [0, 0, set(), set()]

		for message in self.outbox_messages:
			self.messages_dict[str(message.uuid)] = message
			self.mark[str(message.uuid)] = [0, 0, set(), set()]

		self.folders_dict = {}
		self.in_folder = {}
		for folder in self.add_folders:
			self.folders_dict[str(folder.uuid)] = folder
			self.in_folder[str(folder.uuid)] = set()

		for message in AddMessage.objects.all().exclude(folder_id = None):
			try:				
				self.in_folder[str(message.folder_id)].add(message)
				#self.messages_dict[str(message.uuid)] = message
				#self.mark[str(message.uuid)] = [0, 0, set(), set()]
			except:
				print str(message.uuid) + " in " + str(message.folder_id)

		for mark in Readed.objects.all():
			if mark.number >= self.mark[str(mark.message_id)][0]:
				self.mark[str(mark.message_id)][0] = mark.number + 1
			self.mark[str(mark.message_id)][2].add(mark.number)

		for mark in Unreaded.objects.all():
			if mark.number >= self.mark[str(mark.message_id)][1]:
				self.mark[str(mark.message_id)][1] = mark.number + 1
			self.mark[str(mark.message_id)][3].add(mark.number)

		self.op_count = 0
		self.do_flat = False

		self.buffer = Queue.Queue()
		self.queue = Queue.Queue()

		self.add_messages_db = set()
		self.del_messages_db = set()
		self.out_messages_db = set()
		self.add_folders_db = set()
		self.del_folders_db = set()
		self.readed_db = set()
		self.unreaded_db = set()
		
	def add(self, data, queue):
		if queue:
			while settings.FLAT_MANAGER.getFlat():
				print 'FLAT: Block till flatted'
				time.sleep(1)

			self.op_count += 1
			toQueue(data)
		elif settings.FLAT_MANAGER.getCommit():
			self.buffer.put(dict(data))
			return

		obj = self.addToSet(data)
		if obj:
			self.queue.put(obj)

	def addToSet(self, data):
		operation = data.pop('operation')		

		data['uuid'] = uuid.UUID(data['uuid'])

		if operation == 'mark_readed':
			if not self.mark.get(str(data['uuid']), None):
				self.mark[str(data['uuid'])] = [0, 0, set(), set()]

			self.mark[str(data['uuid'])][2].add(data['number'])

			obj = Readed(message_id=data['uuid'], number=data['number'])

			if self.mark[str(data['uuid'])][0] < data['number']+1:
				self.mark[str(data['uuid'])][0] = data['number']+1

			print self.mark[str(data['uuid'])][0]
			print self.mark[str(data['uuid'])][2]			

			return obj

		if operation == 'mark_un_readed':
			if not self.mark.get(str(data['uuid']), None):
				self.mark[str(data['uuid'])] = [0, 0, set(), set()]

			self.mark[str(data['uuid'])][3].add(data['number'])

			obj = Unreaded(message_id=data['uuid'], number=data['number'])

			if self.mark[str(data['uuid'])][1] < data['number']+1:
				self.mark[str(data['uuid'])][1] = data['number']+1

			print self.mark[str(data['uuid'])][1]
			print self.mark[str(data['uuid'])][3]

			return obj

		if operation == 'delete':
			obj = DeleteMessage(**data)
			#obj.save()
			self.delete_messages.add(obj)	

		if operation == 'add_outbox':
			data['author_id'] = uuid.UUID(data['author_id'])
			data['reader_id'] = uuid.UUID(data['reader_id'])
			data['host'] = int(data['host'])
			obj = OutboxMessage(**data)
			#obj.save()
			self.outbox_messages.add(obj)
			if not self.mark.get(str(data['uuid']), None):
				self.mark[str(data['uuid'])] = [0, 0, set(), set()]

		if operation == 'add':
			data['author_id'] = uuid.UUID(data['author_id'])
			data['reader_id'] = uuid.UUID(data['reader_id'])
			data['host'] = int(data['host'])
			data['folder_id'] = None
			obj = AddMessage(**data)
			#obj.save()
			self.messages_dict[str(obj.uuid)] = obj
			self.add_messages.add(obj)
			if not self.mark.get(str(data['uuid']), None):
				self.mark[str(data['uuid'])] = [0, 0, set(), set()]

		if operation == 'add_folder':
			data['user_id'] = uuid.UUID(data['user_id'])
			obj = AddFolder(**data)
			#obj.save()
			self.add_folders.add(obj)
			if not self.in_folder.get(str(obj.uuid), None):
				self.in_folder[str(obj.uuid)] = set()
			self.folders_dict[str(obj.uuid)] = obj

		if operation == 'delete_folder':
			obj = DeleteFolder(**data)
			#obj.save()
			self.delete_folders.add(obj)

		if operation == 'add_to_folder':
			data['author_id'] = uuid.UUID(data['author_id'])
			data['reader_id'] = uuid.UUID(data['reader_id'])
			data['host'] = int(data['host'])
			folder = data['folder_id']
			data['folder_id'] = uuid.UUID(data['folder_id'])

			need_add = data.pop('need_add', None)
			
			obj = AddMessage(**data)

			self.messages_dict[str(obj.uuid)] = obj

			if need_add:
				data.pop('folder_id', None)
				obj_folder_none = AddMessage(**data)
				self.add_messages.add(obj_folder_none)
				self.queue.put(obj_folder_none)
			
			if not self.mark.get(str(data['uuid']), None):
				self.mark[str(data['uuid'])] = [0, 0, set(), set()]


			if not self.in_folder.get(folder, None):
				self.in_folder[folder] = set()	
			
			self.in_folder[folder].add(obj)

		return obj

	def messageReaded(self, uuid):
		print self.mark[str(uuid)][2].difference(self.mark[str(uuid)][3])
		print self.mark[str(uuid)][3].difference(self.mark[str(uuid)][2])
		len_r = len(self.mark[str(uuid)][2])
		len_u = len(self.mark[str(uuid)][3])
		return (len_r - len_u) > 0

	def getOpCount(self):
		return self.op_count

	def getQueueEmpty(self):
		return self.queue.empty()

	def getMessage(self, uuid):
		return self.messages_dict[str(uuid)]

	def getFolder(self, uuid):
		return self.folders_dict[str(uuid)]	

	def getAddMessages(self):
		return set(self.add_messages)

	def getDeleteMessages(self):
		return set(self.delete_messages)

	def getAddFolders(self):
		return set(self.add_folders)

	def getDeleteFolders(self):
		return set(self.delete_folders)

	def getOutboxMessages(self):
		return set(self.outbox_messages)

	def getInFolderALL(self, folder):
		return set(self.in_folder[str(folder)])

	def getInFolder(self, folder):
		current_folder = self.getFolder(folder)
		in_folder = self.in_folder[str(folder)].difference(self.delete_messages)
		for folder in self.getAddFolders():
			if hash(folder) > hash(current_folder):
				in_folder = in_folder.difference(self.in_folder[str(folder.uuid)])
		return in_folder

	def getOutbox(self):
		return self.outbox_messages.difference(self.delete_messages)

	def getFolders(self):
		return self.add_folders.difference(self.delete_folders)

	def getMessages(self):
		messages = self.add_messages.difference(self.delete_messages)
		for folder in self.getAddFolders():
			messages.update(self.in_folder[str(folder)].difference(self.delete_messages))
		return messages

	def getInbox(self):
		inbox = self.add_messages.difference(self.delete_messages)
		for folder in self.getAddFolders():
			inbox = inbox.difference(self.in_folder[str(folder.uuid)])
		return inbox

	def persist_flat(self):
		print '[PERSIST] : start'
		start = time.time()

		Readed.objects.all().delete()
		Unreaded.objects.all().delete()

		for message in OutboxMessage.objects.all():
			if message not in self.outbox_messages:
				message.delete()

		for message in DeleteMessage.objects.all():
			if message not in self.delete_messages:
				message.delete()

		for folder in AddFolder.objects.all():
			if folder not in self.add_folders:
				folder.delete()

		for folder in DeleteFolder.objects.all():
			if folder not in self.add_folders:
				folder.delete()

		for message in AddMessage.objects.filter(folder_id=None):
			if message not in self.add_messages:
				message.delete()
			elif self.messageReaded(message.uuid):
				Readed.objects.create(message_id=message.uuid, number=self.mark[str(message.uuid)][0]-1)

		for message in AddMessage.objects.all().exclude(folder_id=None):
			if not self.folders_dict.get(str(message.folder_id), None):
				message.delete()
			elif message not in self.in_folder[str(message.folder_id)]:
				message.delete()
			#elif self.messageReaded(message.uuid):
			#	Readed.objects.create(message_id=message.uuid, number=1)


		print '[PERSIST] : finished in %s' % str((time.time() - start))

	def persist(self):
		time.sleep(2)
		while(True):
			if self.queue.empty():
				if self.do_flat:
					self.persist_flat()
					self.do_flat = False
				else:
					#print '[PERSIST] : sleeping...'
					time.sleep(1)
			else:
				while self.queue.empty() == False:
					data = self.queue.get()
					data.save()

	def write_state(self, title):
		file_name = 'flat_%s.txt' % str(settings.RUNNING_HOST['id'])

		with open(file_name, 'a') as f:
			f.write(title)
			f.write("Inbox: %s\n" % str(len(self.getInbox())))
			f.write("Outbox: %s\n" % str(len(self.getOutbox())))
			f.write("Folder: %s\n" % str(len(self.getFolders())))
			for fol in self.getFolders():
				f.write("%s: %s\n" % (str(fol.uuid), str(len(self.getInFolder(fol.uuid)))))
			f.write("--- SETS ---\n")
			f.write("AddMessage: %s\n" % str(len(self.add_messages)))
			f.write("DelMessage: %s\n" % str(len(self.delete_messages)))
			f.write("AddFolder: %s\n" % str(len(self.add_folders)))
			f.write("DelFolder: %s\n" % str(len(self.delete_folders)))
			f.write("OutboxMessage: %s\n" % str(len(self.outbox_messages)))

	def flat(self):
		self.write_state("--- BEFORE ---\n")

		# flat in folders
		for folder in self.add_folders:
			self.in_folder[str(folder.uuid)] = self.in_folder[str(folder.uuid)].difference(self.delete_messages)

			for other_folder in self.add_folders:
				if hash(other_folder) > hash(folder):
					self.in_folder[str(folder.uuid)] = self.in_folder[str(folder.uuid)].difference(self.in_folder[str(other_folder.uuid)])

			for message in self.in_folder[str(folder.uuid)]:
				if self.messageReaded(message.uuid):
					self.mark[str(message.uuid)][2] = set()
					self.mark[str(message.uuid)][2].add(self.mark[str(message.uuid)][0]-1)
				else:
					self.mark[str(message.uuid)][2] = set()
				self.mark[str(message.uuid)][3] = set()

		# flat add_messages
		for message in self.add_messages.intersection(self.delete_messages):
			self.add_messages.remove(message)
			self.messages_dict.pop(str(message.uuid), None)
			mark_set = self.mark.pop(str(message.uuid), None)

		# flat outbox_messages
		for message in self.outbox_messages.intersection(self.delete_messages):
			self.outbox_messages.remove(message)
			self.messages_dict.pop(str(message.uuid), None)
			self.mark.pop(str(message.uuid), None)	

		# flat add_folders
		for folder in self.add_folders.intersection(self.delete_folders):
			self.add_folders.remove(folder)
			self.folders_dict.pop(str(folder.uuid), None)
			for message in self.in_folder.pop(str(folder.uuid), None):
				self.add_messages.discard(message)

		# flat marker
		for message in set(self.add_messages):
			if self.messageReaded(message.uuid):
				self.mark[str(message.uuid)][2] = set()
				self.mark[str(message.uuid)][2].add(self.mark[str(message.uuid)][0]-1)
			else:
				self.mark[str(message.uuid)][2] = set()
			self.mark[str(message.uuid)][3] = set()

		# flat delete_messages
		self.delete_messages = set()

		# flat delete_folders
		self.delete_folders = set()

		self.write_state("--- AFTER ---\n")

		self.do_flat = True

		self.op_count = 0

	def clearBuffer(self):
		while not self.buffer.empty():
			print 'buffer clear'
			data = self.buffer.get()
			obj = self.addToSet(data)
			if obj:
				self.queue.put(obj)

def toQueue(data):
	for host in settings.OTHER_HOSTS:
		settings.QUEUE[host['id']].put(dict(**data))

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
			while not settings.QUEUE[host['id']].empty() or settings.SENDER[host['id']].isSending():
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
				print '[COORDINATOR] READY : ALL READY ; SENDING PRE COMMIT'
				self.commit = True
				toQueue(dict(operation='flatten', query='preCommit', host=settings.RUNNING_HOST['id']))				

		if data['query'] == 'ack':
			print '[COORDINATOR] ACK : CHECK IF ALL ACKED'

			self.ack_dict[data['host']] = True

			for host in settings.OTHER_HOSTS:
				if not self.ack_dict[host['id']]:
					print '[COORDINATOR] ACK : NOT ALL ACKED'
					break
			else:
				print '[COORDINATOR] ACK : ALL ACKED ; SENDING COMMIT'
				toQueue(dict(operation='flatten', query='doCommit', host=settings.RUNNING_HOST['id']))
				settings.SET_MANAGER.flat()
				self.clear()
				settings.SET_MANAGER.clearBuffer()
				print '[COORDINATOR] FINISHED'

	def follow(self, data):
		if data['query'] == 'prepare':
			self.flat = True

			print '[FOLLOW] PREPARE : CHECK QUEUE'

			for host in settings.OTHER_HOSTS:
				while not settings.QUEUE[host['id']].empty() or settings.SENDER[host['id']].isSending():
					print '[FOLLOW] PREPARE : QUEUE FULL'
					time.sleep(1)
					pass

			print '[FOLLOW] PREPARE : SENDING READY'

			settings.QUEUE[data['host']].put(dict(operation='flatten', query='ready', host=settings.RUNNING_HOST['id']))

		if data['query'] == 'preCommit':
			print '[FOLLOW] COMMIT : ACKNOWLEDGE'
			self.commit = True
			settings.QUEUE[data['host']].put(dict(operation='flatten', query='ack', host=settings.RUNNING_HOST['id']))
		
		if data['query'] == 'doCommit':
			print '[FOLLOW] COMMIT : FLAT'
			settings.SET_MANAGER.flat()

			print '[FOLLOW] COMMIT : CLEAR'
			self.clear()
			settings.SET_MANAGER.clearBuffer()
			print '[FOLLOW] COMMIT : FINISHED'

		if data['query'] == 'abort':
			print '[FOLLOW] ABORT'
			self.clear()

	def run(self):
		while True:
			try:
				if self.queue.empty():
					if settings.SET_MANAGER.getOpCount() >= 2500 and not self.flat:
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