from django.db import models
from django.utils import timezone

class Number(models.Model):
	title = models.CharField(max_length=10, blank=True)
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