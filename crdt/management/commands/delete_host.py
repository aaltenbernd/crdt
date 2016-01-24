from django.core.management.base import BaseCommand
from django.core.management import call_command

from crdt.models import User, createUser
import ast

class Command(BaseCommand):
	def add_arguments(self, parser):
		parser.add_argument('ID', type=int)

	def handle(self, *args, **options):
		found = False
		host_list = []

		with open("host_list", "r") as f:
			host_list = f.readlines()

		f = open("host_list", "w")

		for line in host_list:
			host = ast.literal_eval(line)
			if host['id'] != options['ID']:
				f.write(str(line))
			else:
				found = True

		f.close()
		
		if found:
			print '>>> Deleted host with id ' + str(options['ID'])
		else:
			print '<<< Host with id ' + str(options['ID']) + ' not found'