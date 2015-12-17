from django.core.management.base import BaseCommand
from django.core.management import call_command


from crdt.models import Host, createUser, createHost

import thread

class Command(BaseCommand):

	def add_arguments(self, parser):
		parser.add_argument('ID', type=int)
	
	def handle(self, *args, **options):
		try:
			self_host = Host.objects.get(host_id=options['ID'])
		except:
			print "\033[91m[[INIT SERVER]"

			call_command("makemigrations")
			call_command("migrate")

			if options['ID'] == 0:
				self_host = createHost(True, 0, 8000)
				createHost(False, 1, 8001)
				createHost(False, 2, 8002)
			if options['ID'] == 1:
				createHost(False, 0, 8000)
				self_host = createHost(True, 1, 8001)
				createHost(False, 2, 8002)
			if options['ID'] == 2:
				createHost(False, 0, 8000)
				createHost(False, 1, 8001)
				self_host = createHost(True, 2, 8002)

			for host in Host.objects.all():
				if host.host_self:
					print 'SELF: ' + str(host) 
				else:
					print 'OTHER: ' + str(host) 

			createUser("anton", "123qwe")
			print 'Created User with username = anton and password = 123qwe'

		call_command('runserver',  str(self_host))