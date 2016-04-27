import uuid

from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
	user = models.OneToOneField(User)
	password = models.CharField(max_length=40)
	uuid = models.UUIDField(primary_key=True, editable=False)

class ReadMarker(models.Model):
	message_id = models.UUIDField(editable=True, default=None, null=True)
	number = models.IntegerField()

class UnreadMarker(models.Model):
	message_id = models.UUIDField(editable=True, default=None, null=True)
	number = models.IntegerField()

class OutboxMessage(models.Model):
	uuid = models.UUIDField(editable=False)
	date = models.CharField(max_length=40)
	text = models.CharField(max_length=40)
	author_id = models.UUIDField(editable=True, default=None, null=True)
	reader_id = models.UUIDField(editable=True, default=None, null=True)
	host = models.IntegerField()

	def __eq__(self, other):
		return self.uuid == other.uuid

	def __hash__(self):
		return int(self.uuid)

	def __str__(self):
		return str(self.uuid)

	def to_dict(self):
		return dict(
			uuid=str(self.uuid),
			text=self.text,
			author_id=str(self.author_id),
			reader_id=str(self.reader_id),
			host=self.host,
			date=self.date,
			operation="add_outbox",
		)

	def getAuthor(self):
		try:
			return UserProfile.objects.get(uuid=self.author_id).user.username
		except:
			return "Not found."

	def getReader(self):
		try:
			return UserProfile.objects.get(uuid=self.reader_id).user.username
		except:
			return "Not found."

class AddMessage(models.Model):
	uuid = models.UUIDField(editable=False)
	date = models.CharField(max_length=40)
	text = models.CharField(max_length=40)
	author_id = models.UUIDField(editable=True, default=None, null=True)
	reader_id = models.UUIDField(editable=True, default=None, null=True)
	host = models.IntegerField()
	folder_id = models.UUIDField(editable=True, default=None, null=True)

	def __eq__(self, other):
		return self.uuid == other.uuid

	def __hash__(self):
		return int(self.uuid)

	def __str__(self):
		return str(self.uuid)

	def to_dict(self):
		return dict(
			uuid=str(self.uuid),
			text=self.text,
			author_id=str(self.author_id),
			reader_id=str(self.reader_id),
			host=self.host,
			date=self.date,
			operation="add",
		)

	def getAuthor(self):
		try:
			return UserProfile.objects.get(uuid=self.author_id).user.username
		except:
			return "Not found."

	def getReader(self):
		try:
			return UserProfile.objects.get(uuid=self.reader_id).user.username
		except:
			return "Not found."

class DeleteMessage(models.Model):
	uuid = models.UUIDField(editable=False)

	def __eq__(self, other):
		return self.uuid == other.uuid

	def __hash__(self):
		return int(self.uuid)

	def __str__(self):
		return str(self.uuid)

	def to_dict(self):
		return dict(
			uuid=str(self.uuid),
			operation="delete"
		)

class AddFolder(models.Model):
	uuid = models.UUIDField(editable=False)
	title = models.CharField(max_length=40)
	user_id = models.UUIDField(editable=True, default=None, null=True)

	def __eq__(self, other):
		return self.uuid == other.uuid

	def __hash__(self):
		return int(self.uuid)
		
	def __str__(self):
		return str(self.uuid)

	def to_dict(self):
		return dict(
			title=self.title,
			user_id=str(self.user_id),
			uuid=str(self.uuid),
			operation="add_folder"
		)

class DeleteFolder(models.Model):
	uuid = models.UUIDField(editable=False)
	
	def __eq__(self, other):
		return self.uuid == other.uuid

	def __hash__(self):
		return int(self.uuid)
		
	def __str__(self):
		return str(self.uuid)

	def to_dict(self):
		return dict(
			uuid=str(self.uuid),
			operation="delete_folder"
		)