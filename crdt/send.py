import time
import requests

from django.conf import settings

# localHost
HOSTNAME = "http://127.0.0.1"

def send_thread(host):
    while True:
        if settings.QUEUE[host['id']].empty():
            time.sleep(1)
        else:
            data = settings.QUEUE[host['id']].get()

            print "[THREAD " + str(host['id']) + "] " + data['operation'] + " to " + str(host['port'])

            while True:
                try:
                    # set up csrftoken, because django needs it
                    URL = HOSTNAME + ":" + str(host['port']) + "/receive/"

                    client = requests.session()
                    client.get(URL)
                    csrftoken = client.cookies['csrftoken']

                    data['csrfmiddlewaretoken'] = csrftoken
                    cookies = dict(client.cookies)

                    # send post request and delete operations
                    r = requests.post(URL, data = data, timeout=5, cookies=cookies)
                    break
                except requests.exceptions.RequestException:
                    time.sleep(2)
                    print "[THREAD " + str(host['id']) + "] Can't reach host " + str(host['port'])
                    continue