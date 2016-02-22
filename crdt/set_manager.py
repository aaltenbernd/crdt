import django
django.setup()

#from .message import AddMessage, DeleteMessage
#from .folder import AddFolder, DeleteFolder
from .models import AddMessage, DeleteMessage, AddFolder, DeleteFolder, OutboxMessage

from django.conf import settings
import uuid
import time
import Queue

class SetManager():
	def __init__(self):
		self.outbox_messages = set(OutboxMessage.objects.all())
		self.add_messages = set(AddMessage.objects.all())
		self.delete_messages = set(DeleteMessage.objects.all())
		self.add_folders = set(AddFolder.objects.all())
		self.delete_folders = set(DeleteFolder.objects.all())

		self.queue = Queue.Queue()
		
	def add(self, data, queue):
		if queue:
			toQueue(data)
		
		obj = self.addToSet(data)
		self.queue.put(obj)

	def addToSet(self, data):
		operation = data.pop('operation')

		data['uuid'] = uuid.UUID(data['uuid'])

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

		if operation == 'add':
			data['author_id'] = uuid.UUID(data['author_id'])
			data['reader_id'] = uuid.UUID(data['reader_id'])
			data['host'] = int(data['host'])
			if data.get('folder', None):
				data['folder'] = uuid.UUID(data['folder'])
			obj = AddMessage(**data)
			#obj.save()
			self.add_messages.add(obj)

		if operation == 'add_folder':
			data['user_id'] = uuid.UUID(data['user_id'])
			obj = AddFolder(**data)
			#obj.save()
			self.add_folders.add(obj)

		if operation == 'delete_folder':
			obj = DeleteFolder(**data)
			#obj.save()
			self.delete_folders.add(obj)

		return obj

	def getQueueEmpty(self):
		return self.queue.empty()		

	def getAddMessages(self):
		return self.add_messages

	def getDeleteMessages(self):
		return self.delete_messages

	def getAddFolders(self):
		return self.add_folders

	def getDeleteFolders(self):
		return self.delete_folders

	def getOutboxMessages(self):
		return self.outbox_messages.difference(self.delete_messages)

	def getMessages(self):
		return self.add_messages.difference(self.delete_messages)

	def getFolders(self):
		return self.add_folders.difference(self.delete_folders)

	def persist(self):
		while(True):
			if self.queue.empty():
				time.sleep(1)
			else:
				while self.queue.empty() == False:
					data = self.queue.get()
					data.save()

def toQueue(data):
	for host in settings.OTHER_HOSTS:
		settings.QUEUE[host['id']].put(dict(**data))