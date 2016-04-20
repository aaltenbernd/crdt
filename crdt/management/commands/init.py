from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
	"""Removes all data from the database givin in the settings file."""

	def handle(self, *args, **options):
		call_command("flush", "--noinput")