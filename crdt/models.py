from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

import uuid

# localHost
HOSTNAME = "http://127.0.0.1"

# used in python manage.py init
# creates a user with given username and passwrd
def createUser(username, password):
	user = User.objects.create_user(username=username, password=password)
	profile = UserProfile.objects.create(user=user)
	user.userprofile = profile
	return

# used in python manage.py init
# creates a none with given id and port
# first argument should be set true, if node is the running host
def createHost(host_self, host_id, port):
	Host.objects.create(host_self=host_self, host_id=host_id, port=port)
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

class AddMessage(models.Model):
	text = models.CharField(max_length=320)
	date = models.DateTimeField(default=timezone.now)
	author = models.CharField(max_length=10, default="myself")
	host_id = models.IntegerField()
	uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

	def __str__(self):
		return 'GLOBAL_ID: ' + str(self.uuid) + ' | HOST_ID: ' + str(self.host_id)

	def to_dict(self, username, operation):
		message_dict = {}
		message_dict['uuid'] = self.uuid
		message_dict['host_id'] = self.host_id
		message_dict['author'] = self.author
		message_dict['text'] = self.text
		message_dict['date'] = str(self.date)
		message_dict['operation'] = operation
		message_dict['username'] = username
		return message_dict

class DeleteMessage(models.Model):
	host_id = models.IntegerField()
	uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

	def __str__(self):
		return 'GLOBAL_ID: ' + str(self.uuid) + ' | HOST_ID: ' + str(self.host_id)

	def to_dict(self, username, operation):
		message_dict = {}
		message_dict['uuid'] = self.uuid
		message_dict['host_id'] = self.host_id		
		message_dict['operation'] = operation
		message_dict['username'] = username
		return message_dict

# saves running (n_self=True) and other hosts (n_self=False)
# n_id have to the same on all hosts in the cluster
class Host(models.Model):
	host_self = models.BooleanField()
	host_id = models.IntegerField()
	port = models.IntegerField()

	def __str__(self):
		return HOSTNAME + ':' + str(self.port)