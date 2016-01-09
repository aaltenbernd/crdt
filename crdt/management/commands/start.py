from django.core.management.base import BaseCommand
from django.core.management import call_command

from crdt.models import createUser

class Command(BaseCommand):	
	def handle(self, *args, **options):
		createUser("anton", "123qwe")