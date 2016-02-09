from django.core.management.base import BaseCommand
from django.core.management import call_command

from crdt.models import User
from crdt.operation import createUser
from django.conf import settings
import os

class Command(BaseCommand):
	def add_arguments(self, parser):
		parser.add_argument('port', type=int)

	def handle(self, *args, **options):
		call_command("makemigrations")

		call_command("migrate")

		call_command('runserver', str(options['port']))