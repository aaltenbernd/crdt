from django.core.management.base import BaseCommand
from django.core.management import call_command

from django.conf import settings

class Command(BaseCommand):
	def handle(self, *args, **options):
		call_command('runserver', '--noreload', str(settings.RUNNING_HOST['port']))