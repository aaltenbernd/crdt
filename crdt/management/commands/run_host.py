from django.core.management.base import BaseCommand
from django.core.management import call_command

from crdt.models import User, createUser
from django.conf import settings
import os

class Command(BaseCommand):
	def handle(self, *args, **options):
		print '>>> Make migrations'
		call_command("makemigrations")

		print '>>> Migrate migrations'
		call_command("migrate")

		print '>>> Create user if neccassary'
		if not User.objects.filter(username="test_user").exists():
			createUser("test_user", "1111")
		print '>>> User exists with username = test_user and password = 1111'

		print '>>> Write host_id file'

		port = settings.RUNNING_HOST['port']

		call_command('runserver', str(port))