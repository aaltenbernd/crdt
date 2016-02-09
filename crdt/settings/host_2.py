from settings import *

import Queue
import thread

from crdt.send import send_thread

ALL_HOSTS = [
				{'id' : 0, 'port' : 8000},
				{'id' : 1, 'port' : 8001},
				{'id' : 2, 'port' : 8002},
			]

RUNNING_HOST = ALL_HOSTS[2]

OTHER_HOSTS = []

for host in ALL_HOSTS:
	if host != RUNNING_HOST:
		OTHER_HOSTS.append(host)

QUEUE = {}
for host in OTHER_HOSTS:
    QUEUE[host['id']] = Queue.Queue()

for host in OTHER_HOSTS:
	thread.start_new_thread(send_thread, (host, ))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'crdt', 'databases', 'db.host.' + str(RUNNING_HOST['id'])),
    }
}