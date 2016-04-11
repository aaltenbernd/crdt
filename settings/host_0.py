from settings import *

import Queue
import thread
 
ALL_HOSTS = [
                {'id' : 0, 'port' : 8000, 'hostname' : "http://127.0.0.1"},
                {'id' : 1, 'port' : 8001, 'hostname' : "http://127.0.0.1"},
                {'id' : 2, 'port' : 8002, 'hostname' : "http://127.0.0.1"},
            ]

RUNNING_HOST = ALL_HOSTS[0]

OTHER_HOSTS = []
SEND_TIME = {}

for host in ALL_HOSTS:
	if host != RUNNING_HOST:
		OTHER_HOSTS.append(host)

QUEUE = {}
for host in OTHER_HOSTS:
    SEND_TIME[host['id']] = float(0)
    QUEUE[host['id']] = Queue.Queue()

SENDER = {}

from crdt.send import Sender
if sys.argv[1] == 'run_host':
    for host in OTHER_HOSTS:
        SENDER[host['id']] = Sender(host['port'], host['hostname'])
        thread.start_new_thread(SENDER[host['id']].run, (host, ))


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'db_host_0',
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

from crdt.set_manager import SetManager, FlatManager
if sys.argv[1] == 'run_host':
    SET_MANAGER = SetManager()
    thread.start_new_thread(SET_MANAGER.persist, ())
    FLAT_MANAGER = FlatManager()
    thread.start_new_thread(FLAT_MANAGER.run, ())
    thread.start_new_thread(SET_MANAGER.write_state, ())