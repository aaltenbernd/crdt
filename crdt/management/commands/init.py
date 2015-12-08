from django.core.management.base import BaseCommand
from django.core.management import call_command

from crdt.models import createUser, createNode

import thread

class Command(BaseCommand):

	def add_arguments(self, parser):
		parser.add_argument('id_A', type=int)
		parser.add_argument('id_B', type=int)
		parser.add_argument('port_A', type=int)
		parser.add_argument('port_B', type=int)
		parser.add_argument('test_user', type=str)
		parser.add_argument('test_pass', type=str)

	
	def handle(self, *args, **options):
		call_command("makemigrations")
		call_command("migrate")

		createNode(True, options['id_A'], options['port_A'])
		print 'Created Node with id = ' + str(options['id_A']) + ' and port = ' + str(options['port_A'])
		createNode(False, options['id_A'], options['port_B'])
		print 'Created Node with id = ' + str(options['id_B']) + ' and port = ' + str(options['port_B'])
		createUser(options['test_user'], options['test_pass'])
		print 'Created User with username = ' + options['test_user'] + ' and password = ' + options['test_pass']