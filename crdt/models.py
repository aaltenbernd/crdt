from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

import uuid

# used in python manage.py init
# creates a user with given username and passwrd
def createUser(username, password):
	user = User.objects.create_user(username=username, password=password)
	profile = UserProfile.objects.create(user=user)
	user.userprofile = profile
	return

# user have a distributed counter
# counter is used for global id in message model
# increment / decrement commutative operations on counter
class UserProfile(models.Model):
	user = models.OneToOneField(User)
	counter = models.IntegerField(default=0)

	def __str__(self):
		return str(self.user) + ":" + str(self.counter)

	def increment(self):
		self.counter = self.counter + 1

	def decrement(self):
		self.counter = self.counter - 1

class AddFolder(models.Model):
	title = models.CharField(max_length=10)
	host_id = models.IntegerField()
	uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

	def __str__(self):
		return self.title

	def to_dict(self, username):
		folder_dict = {}
		folder_dict['uuid'] = self.uuid
		folder_dict['host_id'] = self.host_id
		folder_dict['title'] = self.title
		folder_dict['operation'] = 'add_folder'
		folder_dict['username'] = username
		return folder_dict

class DeleteFolder(models.Model):
	host_id = models.IntegerField()
	uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

	def __str__(self):
		return self.title

	def to_dict(self, username):
		folder_dict = {}
		folder_dict['uuid'] = self.uuid
		folder_dict['host_id'] = self.host_id
		folder_dict['operation'] = 'delete_folder'
		folder_dict['username'] = username
		return folder_dict

class AddMessage(models.Model):
	text = models.CharField(max_length=320)
	date = models.DateTimeField(default=timezone.now)
	author = models.CharField(max_length=10, default="myself")
	host_id = models.IntegerField()
	uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	folder = models.ForeignKey(AddFolder, null=True)

	def __str__(self):
		return 'MESSAGE_GLOBAL_ID: ' + str(self.uuid) + ' | HOST_ID: ' + str(self.host_id)

	def to_dict(self, username, operation):
		message_dict = {}
		message_dict['uuid'] = self.uuid
		message_dict['host_id'] = self.host_id
		message_dict['author'] = self.author
		message_dict['text'] = self.text
		message_dict['date'] = str(self.date)
		message_dict['operation'] = operation
		message_dict['username'] = username
		if self.folder == None:
			message_dict['folder'] = 'None'
		else:
			message_dict['folder'] = self.folder.uuid
		return message_dict

class DeleteMessage(models.Model):
	host_id = models.IntegerField()
	uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

	def __str__(self):
		return 'MESSAGE_GLOBAL_ID: ' + str(self.uuid) + ' | HOST_ID: ' + str(self.host_id)

	def to_dict(self, username, operation):
		message_dict = {}
		message_dict['uuid'] = self.uuid
		message_dict['host_id'] = self.host_id		
		message_dict['operation'] = operation
		message_dict['username'] = username
		return message_dict