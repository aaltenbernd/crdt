from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
import Queue

# localHost
HOSTNAME = "http://127.0.0.1"

def createUser(username, password):
	user = User.objects.create_user(username=username, password=password)
	profile = UserProfile.objects.create(user=user)
	user.userprofile = profile
	return

def createNode(n_self, n_id, port):
	Node.objects.create(n_self=n_self, n_id=n_id, port=port)
	return

# each number saves a title, a value and a date
# increment / decrement are commutative operations
# which can be executed without consider the order
# title is not unique right now
# date saves the creationdate 
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
	message_id = models.IntegerField()
	text = models.CharField(max_length=320)
	date = models.DateTimeField(default=timezone.now)
	author = models.CharField(max_length=10, default="myself")
	host_id = models.IntegerField()
	#reader = models.CharField(max_length=10)

	def __str__(self):
		return 'ID: ' + self.id + ' | HOST_ID: ' + self.host_id

# each node saves the port and the open operations
# the full address of the node is given by str(Node) = http://127.0.0.1:PORT
# the operations have to be send to the HOST
class Node(models.Model):
	n_self = models.BooleanField()
	n_id = models.IntegerField()
	port = models.IntegerField()
	open_ops = models.ManyToManyField('OutgoingOperation', related_name='open_operation', blank=True)

	def __str__(self):
		return HOSTNAME + ':' + str(self.port)

class OutgoingOperation(models.Model):
	data = models.CharField(max_length=400)

	def __str__(self):
		return "Operation: " + self.data

class IncomingOperation(models.Model):
	data = models.CharField(max_length=400)

	def __str__(self):
		return "Incoming: " + self.data