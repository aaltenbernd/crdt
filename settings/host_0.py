from settings import *

import Queue
import thread

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'db_host_0',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
 
if sys.argv[1] == 'run_host' or sys.argv[1] == 'runserver':
    
    ALL_HOSTS = [
                    {'id' : 0, 'port' : 8000, 'hostname' : "http://127.0.0.1"},
                    {'id' : 1, 'port' : 8001, 'hostname' : "http://127.0.0.1"},
                    {'id' : 2, 'port' : 8002, 'hostname' : "http://127.0.0.1"},
                ]

    RUNNING_HOST = ALL_HOSTS[0]

    OTHER_HOSTS = [host for host in ALL_HOSTS if host != RUNNING_HOST]

    SENDER = {}

    from crdt.send import Sender

    for host in OTHER_HOSTS:
        SENDER[host['id']] = Sender(host['port'], host['hostname'])
        thread.start_new_thread(SENDER[host['id']].run, (host, ))

    from crdt.set_manager import SetManager

    SET_MANAGER = SetManager()
    thread.start_new_thread(SET_MANAGER.persist, ())

    from crdt.flat_manager import FlatManager

    FLAT_MANAGER = FlatManager()
    thread.start_new_thread(FLAT_MANAGER.run, ())