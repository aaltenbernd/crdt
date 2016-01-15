from django.core.management.base import BaseCommand
from django.core.management import call_command

from crdt.models import User, createUser

class Command(BaseCommand):
	def add_arguments(self, parser):
		parser.add_argument('ID', type=int)

	def handle(self, *args, **options):
		if not User.objects.filter(username="anton").exists():
			createUser("anton", "123qwe")

		print options['ID']

		with open("host_id", "w") as f:
			f.write(str(options['ID']))