from django.core.management.base import BaseCommand
from django.core.management import call_command

from crdt.models import User, createUser

class Command(BaseCommand):
	def add_arguments(self, parser):
		parser.add_argument('ID', type=int)
		parser.add_argument('PORT', type=int)

	def handle(self, *args, **options):
		with open("host_list", "a") as f:
			f.write("\n{'id' : " + str(options['ID']) + ", 'port' : " + str(options['PORT']) + "}")
			
		print '>>> Added host with id ' + str(options['ID']) + ' and port ' + str(options['PORT'])