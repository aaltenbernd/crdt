from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
import Queue

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
def createNode(n_self, n_id, port):
	Node.objects.create(n_self=n_self, n_id=n_id, port=port)
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

# unique through host_id and global_id
# two messages can have the same global_id one different hosts
# can happen if the hosts are not connected
class Message(models.Model):
	host_id = models.IntegerField()
	global_id = models.IntegerField()
	text = models.CharField(max_length=320)
	date = models.DateTimeField(default=timezone.now)
	author = models.CharField(max_length=10, default="myself")

	def __str__(self):
		return 'GLOBAL_ID: ' + str(self.global_id) + ' | HOST_ID: ' + str(self.host_id)

	# message to dictonary
	# used to send a message with python request
	def to_dict(self, username, operation):
		message_dict = {}

		message_dict['global_id'] = self.global_id
		message_dict['host_id'] = self.host_id
		
		if operation == 'add':
			message_dict['author'] = self.author
			message_dict['text'] = self.text
			message_dict['date'] = str(self.date)
		
		message_dict['operation'] = operation
		message_dict['username'] = username
		return message_dict

# saves running (n_self=True) and other hosts (n_self=False)
# n_id have to the same on all hosts in the cluster
class Node(models.Model):
	n_self = models.BooleanField()
	n_id = models.IntegerField()
	port = models.IntegerField()
	open_ops = models.ManyToManyField('OutgoingOperation', related_name='open_operation', blank=True)

	def __str__(self):
		return HOSTNAME + ':' + str(self.port)

# saves all open outgoing operations as a string
class OutgoingOperation(models.Model):
	data = models.CharField(max_length=400, default="")

# saves all open incoming operations as a string
class IncomingOperation(models.Model):
	data = models.CharField(max_length=400, default="")