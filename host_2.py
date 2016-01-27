from cit_bt_crdt.settings import *

import Queue

ALL_HOSTS = [
				{'id' : 0, 'port' : 8000, 'color' : 'rgba(150, 0, 0, 0.5)'},
				{'id' : 1, 'port' : 8001, 'color' : 'rgba(0, 150, 0, 0.5)'},
				{'id' : 2, 'port' : 8002, 'color' : 'rgba(0, 0, 150, 0.5)'},
			]

RUNNING_HOST = ALL_HOSTS[2]

OTHER_HOSTS = []

for host in ALL_HOSTS:
	if host != RUNNING_HOST:
		OTHER_HOSTS.append(host)

QUEUE = {}
for host in OTHER_HOSTS:
    QUEUE[host['id']] = Queue.Queue()

BAM = "BAM"

# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'crdt', 'databases', 'db.host.' + str(RUNNING_HOST['id'])),
    }
}