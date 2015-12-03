from django.db import models
from django.utils import timezone
import Queue

HOSTNAME = "http://127.0.0.1"

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

class Node(models.Model):
	port = models.IntegerField(default="8000")
	open_ops = models.ManyToManyField('Operation', related_name='open_operation')

	def __str__(self):
		return HOSTNAME + ':' + str(self.port)

class Operation(models.Model):
	operation = models.CharField(max_length=20)
	num = models.ForeignKey(Number, related_name='num_op')

	def __str__(self):
		return "Operation: " + self.operation + " to " + str(self.num)