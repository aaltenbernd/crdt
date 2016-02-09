from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

import uuid

class UserProfile(models.Model):
	user = models.OneToOneField(User)
	uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

class AddFolder(models.Model):
	title = models.CharField(max_length=10)
	host_id = models.IntegerField()
	uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	user_uuid = models.UUIDField(editable=True, default=None, null=True)

	def __str__(self):
		return self.title

	def to_dict(self):
		folder_dict = {}
		folder_dict['uuid'] = self.uuid
		folder_dict['host_id'] = self.host_id
		folder_dict['title'] = self.title
		folder_dict['operation'] = 'add_folder'
		folder_dict['user_uuid'] = self.user_uuid
		return folder_dict

class DeleteFolder(models.Model):
	host_id = models.IntegerField()
	uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	user_uuid = models.UUIDField(editable=True, default=None, null=True)

	def __str__(self):
		return self.uuid

	def to_dict(self):
		folder_dict = {}
		folder_dict['uuid'] = self.uuid
		folder_dict['host_id'] = self.host_id
		folder_dict['operation'] = 'delete_folder'
		folder_dict['user_uuid'] = self.user_uuid
		return folder_dict

class AddMessage(models.Model):
	text = models.CharField(max_length=320)
	date = models.DateTimeField(default=timezone.now)
	author = models.CharField(max_length=10, default="myself")
	reader = models.CharField(max_length=10, default="myself")
	author_uuid = models.UUIDField(editable=True, default=None, null=True)
	reader_uuid = models.UUIDField(editable=True, default=None, null=True)
	host_id = models.IntegerField()
	uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	folder_id = models.UUIDField(editable=True, default=None, null=True)
	color = models.CharField(max_length=30)
	inbox = models.BooleanField(default=True)

	def __str__(self):
		return 'MESSAGE_GLOBAL_ID: ' + str(self.uuid) + ' | HOST_ID: ' + str(self.host_id)

	def to_dict(self):
		message_dict = {}
		message_dict['uuid'] = self.uuid
		message_dict['host_id'] = self.host_id
		message_dict['author'] = self.author
		message_dict['author_uuid'] = self.author_uuid
		message_dict['reader'] = self.reader
		message_dict['reader_uuid'] = self.reader_uuid
		message_dict['text'] = self.text
		message_dict['date'] = str(self.date)
		message_dict['folder_id'] = self.folder_id
		message_dict['color'] = self.color
		message_dict['inbox'] = self.inbox
		message_dict['operation'] = "add"
		return message_dict

class DeleteMessage(models.Model):
	author = models.CharField(max_length=10, default="myself")
	reader = models.CharField(max_length=10, default="myself")
	author_uuid = models.UUIDField(editable=True, default=None, null=True)
	reader_uuid = models.UUIDField(editable=True, default=None, null=True)
	host_id = models.IntegerField()
	uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

	def __str__(self):
		return 'MESSAGE_GLOBAL_ID: ' + str(self.uuid) + ' | HOST_ID: ' + str(self.host_id)

	def to_dict(self):
		message_dict = {}
		message_dict['uuid'] = self.uuid
		message_dict['host_id'] = self.host_id
		message_dict['author'] = self.author
		message_dict['reader'] = self.reader
		message_dict['author_uuid'] = self.author_uuid
		message_dict['reader_uuid'] = self.reader_uuid
		message_dict['operation'] = "delete"
		return message_dict