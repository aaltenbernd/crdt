import requests
import time
import ast
import json
import random
import sys

HOST = "http://127.0.0.1"
PORT = ["8000", "8001", "8002"]

def url(host, port, operation):
	return host + ":" + port + "/" + operation

class Test():
	def __init__(self, port):
		self.port = port
		self.username = None
		self.password = None
		self.response = None
		self.sessionid = None

		self.client = requests.session()
		# only needed if csrf token is necessary
		self.url = "http://127.0.0.1:" + str(self.port)
		self.client.get(self.url)
		self.csrftoken = self.client.cookies['csrftoken']
		self.cookies = dict(self.client.cookies)

	def register(self, username, password, password_confirm):
		self.url = url(HOST, self.port, "api_register")
		self.post_data = dict(username=username, password=password, password_confirm=password_confirm, csrfmiddlewaretoken=self.csrftoken)
		self.response = self.client.post(self.url, self.post_data, cookies=self.cookies)
		self.username = username
		self.password = password

	def login(self, username, password):
		self.url = url(HOST, self.port, "api_login")
		self.post_data = dict(username=username, password=password, csrfmiddlewaretoken=self.csrftoken)
		self.response = self.client.post(self.url, self.post_data, cookies=self.cookies)
		self.sessionid = self.client.cookies['sessionid']
		self.csrftoken = self.client.cookies['csrftoken']
		self.cookies = dict(self.client.cookies)
		self.username = username
		self.password = password

	def logout(self):
		self.url = url(HOST, self.port, "api_logout")
		self.response = self.client.get(self.url)

	def addMessage(self, text):
		self.url = url(HOST, self.port, "api_addMessage")
		self.post_data = dict(sessionid=self.sessionid, text=text, reader=self.username, csrfmiddlewaretoken=self.csrftoken)
		self.response = self.client.post(self.url, self.post_data, cookies=self.cookies)

	def deleteMessage(self, uuid):
		self.url = url(HOST, self.port, "api_deleteMessage")
		self.url = self.url + "/" + str(uuid) + "/"
		self.response = self.client.get(self.url)

	def getCurrentState(self):
		self.url = url(HOST, self.port, "api_getCurrentState")
		self.response = self.client.get(self.url)

	def getQueue(self):
		self.url = url(HOST, self.port, "api_getQueue")
		self.response = self.client.get(self.url)

	def getSetManagerQueue(self):
		self.url = url(HOST, self.port, "api_getSetManagerQueue")
		self.response = self.client.get(self.url)

	def addFolder(self, title):
		self.url = url(HOST, self.port, "api_addFolder")
		self.post_data = dict(sessionid=self.sessionid, title=title, csrfmiddlewaretoken=self.csrftoken)
		self.response = self.client.post(self.url, self.post_data, cookies=self.cookies)

	def deleteFolder(self, uuid):
		self.url = url(HOST, self.port, "api_deleteFolder")
		self.url = self.url + "/" + str(uuid) + "/"
		self.response = self.client.get(self.url)

	def changeFolder(self, folder_uuid, message_uuid):
		self.url = url(HOST, self.port, "api_changeFolder")
		self.url = self.url + "/" + str(message_uuid) + "/"
		self.post_data = dict(sessionid=self.sessionid, folder_choice=folder_uuid, csrfmiddlewaretoken=self.csrftoken)
		self.response = self.client.post(self.url, self.post_data, cookies=self.cookies)

	def waitForHost(self):
		self.getQueue()
		return json.loads(self.response.content)

	def waitForPersist(self):
		self.getSetManagerQueue()
		return json.loads(self.response.content)

	def getState(self):
		self.url = url(HOST, self.port, "api_getState")
		self.response = self.client.get(self.url)
		return json.loads(self.response.content)

	def getMessages(self):
		self.url = url(HOST, self.port, "api_getMessages")
		self.response = self.client.get(self.url)
		return json.loads(self.response.content)

	def getFolders(self):
		self.url = url(HOST, self.port, "api_getFolders")
		self.response = self.client.get(self.url)
		return json.loads(self.response.content)

	def getSendTime(self):
		self.url = url(HOST, self.port, "api_getSendTime")
		self.response = self.client.get(self.url)
		return json.loads(self.response.content)

if __name__ == '__main__':
	if len(sys.argv) != 2 and len(sys.argv) != 3:
		print "[TEST] Pick a amount of operation."
		sys.exit(1)

	try:
		amount_op = int(sys.argv[1])
	except:
		print "[TEST] Pick a int as amount of operation."
		sys.exit(1)

	print "[TEST] Starting crdt mail service test with " + sys.argv[1] + " random operations.\n"

	try:
		test_0 = Test(PORT[0])
	except:
		print "[TEST] Host 0 is not online..."
		sys.exit(1)
	try:
		test_1 = Test(PORT[1])
	except:
		print "[TEST] Host 1 is not online..."
		sys.exit(1)
	try:
		test_2 = Test(PORT[2])
	except:
		print "[TEST] Host 2 is not online..."
		sys.exit(1)

	print sys.argv[1]
	if int(sys.argv[1]) == -1:
		print "[TEST] Register user on one host."
		test_0.register('test_user', '1111', '1111')
		sys.exit(1)

	print "[TEST] Login user on each host.\n"
	test_0.login('test_user', '1111')
	test_1.login('test_user', '1111')
	test_2.login('test_user', '1111')	

	hst_list = [test_0, test_1, test_2]

	time_result = 0
	count_result = [0, 0, 0, 0, 0]

	del_msg = []
	del_fol = []

	op = ['add', 'add_folder', 'delete', 'delete_folder', 'change_folder']

	i = 0
	while i < amount_op:
		host = hst_list[random.randint(0,2)]		

		try:
			operation = int(sys.argv[2])
		except:
			operation = random.choice([0, 1, 2, 3])

		# addMessage
		if operation == 0:
			op_start = time.time()
			host.addMessage(i)

		# addFolder
		if operation == 1:
			op_start = time.time()
			host.addFolder(i)
			
		# deleteMessage
		if operation == 2:
			msg_list = host.getMessages()
			if not msg_list:
				continue
			msg = random.choice(msg_list)

			if msg in del_msg:
				continue
			else:
				del_msg.append(msg)

			op_start = time.time()
			host.deleteMessage(msg)

		# deleteFolder
		if operation == 3:
			fol_list = host.getFolders()
			if not fol_list:
				continue
			fol = random.choice(fol_list)
			if fol in del_fol:
				continue
			else:
				del_fol.append(fol)

			op_start = time.time()
			host.deleteFolder(fol)

		# changeFolder
		if operation == 4:
			msg_list = host.getMessages()
			fol_list = host.getFolders()
			if not msg_list:
				continue
			msg = random.choice(msg_list)
			fol_with_inbox = []
			fol_with_inbox.extend(fol_list)
			fol_with_inbox.append('Inbox')
			fol = random.choice(fol_with_inbox)
			if msg in del_msg or fol in del_fol:
				continue
			else:
				del_msg.append(msg)

			op_start = time.time()
			host.changeFolder(fol, msg)
			
		op_end = json.loads(host.response.content)['time']
		#op_end = time.time() - op_start
		time_result += op_end
		print '[TEST] %.4f seconds : %s' % (op_end, op[operation]) # + " seconds : " + op[operation]
		count_result[operation] += 1

		if host.response.status_code != 200:
			print host.response.status_code
			sys.exit()
		elif json.loads(host.response.content)['error']:
			print str(operation)
			print json.loads(host.response.content)['message']

		if i >= 10 and i % (amount_op/(amount_op/10)) == 0:
			percent = int(float(i) / float(amount_op) * 100)
			print '\n[TEST] ' + str(percent) + ' %\tcompleted\n'

		i += 1

	if i != 0:
		percent = int(float(i) / float(amount_op) * 100)
		print '\n[TEST] ' + str(percent) + ' %\tcompleted\n'

		x = 0
		while test_0.waitForHost() or test_1.waitForHost() or test_2.waitForHost():
			if x == 100:
				print "[TEST] Waiting for host queue."
				x = 0
			else:
				x += 1
			pass

		print ""

		count = 0
		for c in count_result:
			count += c

		count += count_result[0] # outbox messages!
		count += count_result[4] # x2 delete and add

		print "[TEST] " + str(count_result[0]) + " AddMessage operation."
		print "[TEST] " + str(count_result[1]) + " AddFolder operation."
		print "[TEST] " + str(count_result[2]) + " DeleteMessage operation."
		print "[TEST] " + str(count_result[3]) + " DeleteFolder operation."
		print "[TEST] " + str(count_result[4]) + " MoveMessage operation."
		print "[TEST] makes " + str(count) + " operation.\n"
			
		print "[TEST] It took %.6f seconds." % time_result
		print "[TEST] It took %.6f seconds per operation.\n" % float(time_result/count)

		x = 0
		while test_0.waitForPersist() or test_1.waitForPersist() or test_2.waitForPersist():
			if x == 100:
				print "[TEST] Waiting for host to persist."
				x = 0
			else:
				x += 1
			pass

	dist_time = test_0.getSendTime()['time'] + test_1.getSendTime()['time'] + test_2.getSendTime()['time']
	dist_time = dist_time/float(3)

	print "\n[TEST] Time for sending in sending thread : " + str(dist_time) + "\n"

	state_0 = test_0.getState()
	add_msg_set_0 = set()
	for msg in state_0['add_messages']:
		add_msg_set_0.add((msg[0], msg[1]))
	del_msg_set_0 = set(json.loads(test_0.response.content)['delete_messages'])
	add_fol_set_0 = set(json.loads(test_0.response.content)['add_folders'])
	del_fol_set_0 = set(json.loads(test_0.response.content)['delete_folders'])
	out_box_set_0 = set(json.loads(test_0.response.content)['outbox_messages'])

	state_1 = test_1.getState()
	add_msg_set_1 = set()
	for msg in state_1['add_messages']:
		add_msg_set_1.add((msg[0], msg[1]))
	del_msg_set_1 = set(json.loads(test_1.response.content)['delete_messages'])
	add_fol_set_1 = set(json.loads(test_1.response.content)['add_folders'])
	del_fol_set_1 = set(json.loads(test_1.response.content)['delete_folders'])
	out_box_set_1 = set(json.loads(test_1.response.content)['outbox_messages'])

	state_2 = test_2.getState()
	add_msg_set_2 = set()
	for msg in state_2['add_messages']:
		add_msg_set_2.add((msg[0], msg[1]))
	del_msg_set_2 = set(json.loads(test_2.response.content)['delete_messages'])
	add_fol_set_2 = set(json.loads(test_2.response.content)['add_folders'])
	del_fol_set_2 = set(json.loads(test_2.response.content)['delete_folders'])
	out_box_set_2 = set(json.loads(test_2.response.content)['outbox_messages'])

	if add_msg_set_0 == add_msg_set_1 == add_msg_set_2:
		print '[TEST] Passed addMessage check - got ' + str(len(add_msg_set_0)) + ' addMessage.'

	if del_msg_set_0 == del_msg_set_1 == del_msg_set_2:
		print '[TEST] Passed delMessage check - got ' + str(len(del_msg_set_0)) + ' delMessage.'

	if add_fol_set_0 == add_fol_set_1 == add_fol_set_2:
		print '[TEST] Passed addFolder check - got ' + str(len(add_fol_set_0)) + ' addFolder.'

	if del_fol_set_0 == del_fol_set_1 == del_fol_set_2:
		print '[TEST] Passed delFolder check - got ' + str(len(del_fol_set_0)) + ' delFolder.'

	if out_box_set_0 == out_box_set_1 == out_box_set_2:
		print '[TEST] Passed outboxMessage check - got ' + str(len(out_box_set_0)) + ' outboxMessage.'

	all_len = len(add_msg_set_0) + len(del_msg_set_0) + len(add_fol_set_0) + len(del_fol_set_0) + len(out_box_set_0)

	print '[TEST] makes ' + str(all_len) + ' saves.'

	print "\n[TEST] Logout user on each host.\n"
	test_0.logout()
	test_1.logout()
	test_2.logout()