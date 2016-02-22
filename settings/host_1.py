from settings import *

import Queue
import thread
 
ALL_HOSTS = [
                {'id' : 0, 'port' : 8000},
                {'id' : 1, 'port' : 8001},
                {'id' : 2, 'port' : 8002},
            ]

RUNNING_HOST = ALL_HOSTS[1]

OTHER_HOSTS = []
SEND_TIME = {}

for host in ALL_HOSTS:
    if host != RUNNING_HOST:
        OTHER_HOSTS.append(host)

QUEUE = {}
for host in OTHER_HOSTS:
    SEND_TIME[host['id']] = float(0)
    QUEUE[host['id']] = Queue.Queue()

from crdt.send import send_thread
if sys.argv[1] == 'run_host':
    for host in OTHER_HOSTS:
        thread.start_new_thread(send_thread, (host, ))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'db_host_1',
        'USER': 'Anton',
        'PASSWORD': '351344',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

'''DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'crdt', 'databases', 'db.host.' + str(RUNNING_HOST['id'])),
    }
}'''

from crdt.set_manager import SetManager
if sys.argv[1] == 'run_host':
    SET_MANAGER = SetManager()
    thread.start_new_thread(SET_MANAGER.persist, ())