import time
import requests
import json
import Queue

from django.conf import settings
from random import shuffle

BATCH_SIZE = 1

class Sender():
    """
    Sending thread class.
    Including attributs for http posts and a operation queue.
    """

    def __init__(self, port, hostname):
        self.port = port
        self.client = requests.session()
        self.url = hostname + ":" + str(port) + "/receive/"
        self.csrftoken = None
        self.cookies = None
        self.post_data = None
        self.response = None
        self.count = 0
        self.old_qsize = 0
        self.sending = True
        self.queue = Queue.Queue()

    def send_post(self, data):
        """Sending a post request with given data."""

        self.post_data = data
        self.post_data['csrfmiddlewaretoken'] = self.csrftoken
        self.response = self.client.post(self.url, self.post_data, cookies=self.cookies)

    def isSending(self):
        return self.sending

    def run(self, host):
        """Periodically sends operations to the given host."""

        # Trying to connect to given host.
        while self.csrftoken == None:
            try:
                self.client.get(self.url)
                self.csrftoken = self.client.cookies['csrftoken']
                self.cookies = dict(self.client.cookies)
            except:
                pass

        while True:
            if self.queue.empty():
                self.sending = False
                time.sleep(1)
            else:
                self.sending = True

                # sending operations when queue reached batching size
                # after about 5 seconds send anyway...
                qsize = self.queue.qsize()
                if qsize < BATCH_SIZE and qsize != self.old_qsize:
                    time.sleep(1)
                    self.old_qsize = qsize
                elif qsize < BATCH_SIZE and qsize == self.old_qsize and self.count < 5:
                    time.sleep(1)
                    self.count += 1
                else:
                    data_list = []
                    while not self.queue.empty():
                        op = self.queue.get()
                        data_list.append(op)
                        # just for testing
                        # shuffle(data_list)
                    data_dict = dict(list=json.dumps(data_list))  

                    while True:
                        try:
                            self.send_post(data_dict)
                            break
                        except requests.exceptions.RequestException:
                            time.sleep(2)
                            print "[THREAD " + str(host['id']) + "] Can't reach host " + str(host['port'])
                            continue

                    self.count = 0

def toQueue(data):
    """Adds a operation to all queues of the sending threads."""

    for host in settings.OTHER_HOSTS:
        settings.SENDER[host['id']].queue.put(dict(**data))