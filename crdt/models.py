from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
import Queue

# localHost
HOSTNAME = "http://127.0.0.1"

# used in python manage.py init
def createUser(username, password):
	user = User.objects.create_user(username=username, password=password)
	profile = UserProfile.objects.create(user=user)
	user.userprofile = profile
	return

# used in python manage.py init
def createNode(n_self, n_id, port):
	Node.objects.create(n_self=n_self, n_id=n_id, port=port)
	return

class UserProfile(models.Model):
	user = models.OneToOneField(User)
	counter = models.IntegerField(default=0)

	def __str__(self):
		return str(self.user) + ":" + str(self.counter)

	def increment(self):
		self.counter = self.counter + 1

	def decrement(self):
		self.counter = self.counter - 1

class Message(models.Model):
	host_id = models.IntegerField()
	global_id = models.IntegerField()
	text = models.CharField(max_length=320)
	date = models.DateTimeField(default=timezone.now)
	author = models.CharField(max_length=10, default="myself")

	def __str__(self):
		return 'GLOBAL_ID: ' + str(self.global_id) + ' | HOST_ID: ' + str(self.host_id)

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

class Node(models.Model):
	n_self = models.BooleanField()
	n_id = models.IntegerField()
	port = models.IntegerField()
	open_ops = models.ManyToManyField('OutgoingOperation', related_name='open_operation', blank=True)

	def __str__(self):
		return HOSTNAME + ':' + str(self.port)

class OutgoingOperation(models.Model):
	data = models.CharField(max_length=400, default="")

	def __str__(self):
		return "Outgoing: " + self.data

class IncomingOperation(models.Model):
	data = models.CharField(max_length=400, default="")

	def __str__(self):
		return "Incoming: " + self.data