from django.core.management.base import BaseCommand
from django.core.management import call_command

from crdt.models import User, createUser
import ast

class Command(BaseCommand):
	def add_arguments(self, parser):
		parser.add_argument('ID', type=int)

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

		with open("host_id", "w") as f:
			f.write(str(options['ID']))

		port = -1

		print '>>> Get port of host with ID ', options['ID']

		with open("host_list", "r") as f:
			for line in f:
				host = ast.literal_eval(line)
				if host['id'] == options['ID']:
					port = host['port']

		if port == -1:
			print '<<< ID not found'
			return
		else:
			print '>>> Start server with port ', port

		call_command('runserver',  str(port))