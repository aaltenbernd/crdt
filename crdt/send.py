import time
import requests
import json

from django.conf import settings

# localHost
HOSTNAME = "http://127.0.0.1"
BATCH_SIZE = 50

class Sender():
    def __init__(self, port):
        self.port = port
        self.client = requests.session()
        self.url = HOSTNAME + ":" + str(port) + "/receive/"
        self.client.get(self.url)
        self.csrftoken = self.client.cookies['csrftoken']
        self.cookies = dict(self.client.cookies)
        self.post_data = None
        self.response = None
        self.count = 0
        self.send_count = 0
        self.total_time = float(0)
        self.old_qsize = 0

    def send_post(self, data):
        self.post_data = data
        self.post_data['csrfmiddlewaretoken'] = self.csrftoken
        self.response = self.client.post(self.url, self.post_data, cookies=self.cookies)

def send_thread(host):
    sender = None
    while sender == None:
        try:
            sender = Sender(host['port'])
        except:
            pass

    while True:
        if settings.QUEUE[host['id']].empty():
            time.sleep(1)
            if sender.send_count > 0:
                settings.SEND_TIME[host['id']] = float(sender.total_time)/float(sender.send_count)
        else:
            qsize = settings.QUEUE[host['id']].qsize()
            if qsize < BATCH_SIZE and qsize != sender.old_qsize:
                time.sleep(1)
                sender.old_qsize = qsize
            elif qsize < BATCH_SIZE and qsize == sender.old_qsize and sender.count < 3:
                time.sleep(1)
                sender.count += 1
            else:
                data_list = []
                while not settings.QUEUE[host['id']].empty():
                    data_list.append(settings.QUEUE[host['id']].get())
                    sender.send_count += 1
                data_dict = dict(list=json.dumps(data_list))

                print '[SEND]'

                while True:
                    try:
                        #sender = Sender(host['port'])
                        send_start = time.time()
                        sender.send_post(data_dict)
                        send_end = time.time() - send_start
                        sender.total_time += send_end

                        break
                    except requests.exceptions.RequestException:
                        time.sleep(2)
                        print "[THREAD " + str(host['id']) + "] Can't reach host " + str(host['port'])
                        continue

                sender.count = 0     