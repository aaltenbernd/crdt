import Queue
import ast

all_hosts = []
other_hosts = []
running_host = {}
own_id = 0

try:
	with open("host_id", "r") as f:
		own_id = f.readline()
except IOError:
	print "host_id file don't exist!"

try:
	with open("host_list", "r") as f:
		for line in f:
			host = ast.literal_eval(line)
			all_hosts.append(host)
			if int(host['id']) != int(own_id):
				other_hosts.append(host)
			else:
				running_host = host
except IOError:
	print "host_list file don't exist!"

queue = {}
for host in other_hosts:
    queue[host['id']] = Queue.Queue()