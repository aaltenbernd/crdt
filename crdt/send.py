import time
import requests
import json

from django.conf import settings

from random import shuffle

BATCH_SIZE = 1

class Sender():
    def __init__(self, port, hostname):
        self.port = port
        self.client = requests.session()
        self.url = hostname + ":" + str(port) + "/receive/"
        self.csrftoken = None
        self.cookies = None
        self.post_data = None
        self.response = None
        self.count = 0
        self.send_count = 0
        self.total_time = float(0)
        self.old_qsize = 0
        self.sending = True

    def send_post(self, data):
        self.post_data = data
        self.post_data['csrfmiddlewaretoken'] = self.csrftoken
        self.response = self.client.post(self.url, self.post_data, cookies=self.cookies)

    def isSending(self):
        return self.sending

    def run(self, host):

        while self.csrftoken == None:
            try:
                self.client.get(self.url)
                self.csrftoken = self.client.cookies['csrftoken']
                self.cookies = dict(self.client.cookies)
            except:
                pass

        while True:
            if settings.QUEUE[host['id']].empty():
                self.sending = False
                time.sleep(1)
                if self.send_count > 0:
                    settings.SEND_TIME[host['id']] = float(self.total_time)/float(self.send_count)
            else:
                self.sending = True

                qsize = settings.QUEUE[host['id']].qsize()
                if qsize < BATCH_SIZE and qsize != self.old_qsize:
                    time.sleep(1)
                    self.old_qsize = qsize
                elif qsize < BATCH_SIZE and qsize == self.old_qsize and self.count < 5:
                    time.sleep(1)
                    self.count += 1
                else:
                    data_list = []
                    while not settings.QUEUE[host['id']].empty():
                        op = settings.QUEUE[host['id']].get()
                        data_list.append(op)
                        shuffle(data_list)
                        self.send_count += 1
                    data_dict = dict(list=json.dumps(data_list))  

                    while True:
                        try:
                            send_start = time.time()
                            self.send_post(data_dict)
                            send_end = time.time() - send_start
                            self.total_time += send_end

                            break
                        except requests.exceptions.RequestException:
                            time.sleep(2)
                            print "[THREAD " + str(host['id']) + "] Can't reach host " + str(host['port'])
                            continue

                    self.count = 0