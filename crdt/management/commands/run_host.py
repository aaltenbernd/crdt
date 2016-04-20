from django.core.management.base import BaseCommand
from django.core.management import call_command

from django.conf import settings

class Command(BaseCommand):
	"""Starts a local host with the port in the given settings file."""

	def add_arguments(self, parser):

		parser.add_argument('--production',
							action='store_true',
							dest='ENV',
							default=False,
							help='Set environment to production.')

	def handle(self, *args, **options):

		if options['ENV']:
			call_command('runserver', '--noreload', "0.0.0.0:8000")
		else:
			call_command('runserver', '--noreload', str(settings.RUNNING_HOST['port']))