from django.db import models
from django.utils import timezone
import Queue

# localHost
HOSTNAME = "http://127.0.0.1"

# each number saves a title, a value and a date
# increment / decrement are commutative operations
# which can be executed without consider the order
# title is not unique right now
# date saves the creationdate 
class Number(models.Model):
	title = models.CharField(max_length=10, blank=True, unique=True)
	number = models.IntegerField(default=0)
	date = models.DateTimeField(default=timezone.now)

	def __str__(self):
		return str(self.title)

	def increment(self):
		self.number = self.number + 1

	def decrement(self):
		self.number = self.number - 1

	def delete(self, *args, **kwargs):
		super(Number, self).delete(*args, **kwargs)

# each node saves the port and the open operations
# the full address of the node is given by str(Node) = http://127.0.0.1:PORT
# the operations have to be send to the HOST
class Node(models.Model):
	port = models.IntegerField(default="8000")
	open_ops = models.ManyToManyField('OutgoingOperation', related_name='open_operation', blank=True)

	def __str__(self):
		return HOSTNAME + ':' + str(self.port)

# saves the open operation which has to be send to other hosts
class OutgoingOperation(models.Model):
	operation = models.CharField(max_length=20)
	num = models.CharField(max_length=10)

	def __str__(self):
		return "Operation: " + self.operation + " to " + self.num

# saves the open operation which has to be executed
class IncomingOperation(models.Model):
	operation = models.CharField(max_length=20)
	num = models.CharField(max_length=10)

	def __str__(self):
		return "Operation: " + self.operation + " to " + self.num