import requests
import time
import json
import random
import sys
import os

try:
    os.environ['ENV']
except:
	os.environ['ENV'] = "development"

if os.environ['ENV'] == "production":
	ALL_HOSTS = [
	                {'id' : 0, 'port' : 8000, 'hostname' : "http://52.58.101.237"},
	                {'id' : 1, 'port' : 8000, 'hostname' : "http://52.29.172.155"},
	                {'id' : 2, 'port' : 8000, 'hostname' : "http://52.28.25.55"},
	            ]
else:
	ALL_HOSTS = [
	                {'id' : 0, 'port' : 8000, 'hostname' : 'http://127.0.0.1'},
	                {'id' : 1, 'port' : 8001, 'hostname' : 'http://127.0.0.1'},
	                {'id' : 2, 'port' : 8002, 'hostname' : 'http://127.0.0.1'},
	            ]

def url(host, port, operation):
	return host + ":" + str(port) + "/" + operation

class Client():
	def __init__(self, port, hostname):
		self.port = port
		self.hostname = hostname
		self.username = None
		self.password = None
		self.response = None
		self.sessionid = None

		self.client = requests.session()
		# only needed if csrf token is necessary
		self.url = self.hostname + ":" + str(self.port)
		self.client.get(self.url)
		self.csrftoken = self.client.cookies['csrftoken']
		self.cookies = dict(self.client.cookies)

	def __str__(self):
		return host + ":" + port

	def register(self, username, password, password_confirm):
		self.url = url(self.hostname, self.port, "api_register")
		self.post_data = dict(username=username, password=password, password_confirm=password_confirm, csrfmiddlewaretoken=self.csrftoken)
		self.response = self.client.post(self.url, self.post_data, cookies=self.cookies)
		self.username = username
		self.password = password

	def login(self, username, password):
		self.url = url(self.hostname, self.port, "api_login")
		self.post_data = dict(username=username, password=password, csrfmiddlewaretoken=self.csrftoken)
		self.response = self.client.post(self.url, self.post_data, cookies=self.cookies)
		self.sessionid = self.client.cookies['sessionid']
		self.csrftoken = self.client.cookies['csrftoken']
		self.cookies = dict(self.client.cookies)
		self.username = username
		self.password = password

	def logout(self):
		self.url = url(self.hostname, self.port, "api_logout")
		self.response = self.client.get(self.url)

	def addMessage(self, text):
		self.url = url(self.hostname, self.port, "api_addMessage")
		self.post_data = dict(sessionid=self.sessionid, text=text, reader=self.username, csrfmiddlewaretoken=self.csrftoken)
		self.response = self.client.post(self.url, self.post_data, cookies=self.cookies)

	def deleteMessage(self, message_id):
		self.url = url(self.hostname, self.port, "api_deleteMessage")
		self.post_data = dict(sessionid=self.sessionid, message_id=message_id, csrfmiddlewaretoken=self.csrftoken)
		self.response = self.client.post(self.url, self.post_data, cookies=self.cookies)

	def addFolder(self, title):
		self.url = url(self.hostname, self.port, "api_addFolder")
		self.post_data = dict(sessionid=self.sessionid, title=title, csrfmiddlewaretoken=self.csrftoken)
		self.response = self.client.post(self.url, self.post_data, cookies=self.cookies)

	def deleteFolder(self, folder_id):
		self.url = url(self.hostname, self.port, "api_deleteFolder")
		self.post_data = dict(sessionid=self.sessionid, folder_id=folder_id, csrfmiddlewaretoken=self.csrftoken)
		self.response = self.client.post(self.url, self.post_data, cookies=self.cookies)

	def changeFolder(self, folder_choice, old_folder, message_id):
		self.url = url(self.hostname, self.port, "api_changeFolder")
		self.post_data = dict(sessionid=self.sessionid, message_id=message_id, folder_choice=folder_choice, old_folder=old_folder, csrfmiddlewaretoken=self.csrftoken)
		self.response = self.client.post(self.url, self.post_data, cookies=self.cookies)

	def mark_readed(self, message_id):
		self.url = url(self.hostname, self.port, "api_mark_readed")
		self.post_data = dict(sessionid=self.sessionid, message_id=message_id, csrfmiddlewaretoken=self.csrftoken)
		self.response = self.client.post(self.url, self.post_data, cookies=self.cookies)
	
	def mark_unreaded(self, message_id):
		self.url = url(self.hostname, self.port, "api_mark_unreaded")
		self.post_data = dict(sessionid=self.sessionid, message_id=message_id, csrfmiddlewaretoken=self.csrftoken)
		self.response = self.client.post(self.url, self.post_data, cookies=self.cookies)

	def getWait(self):
		self.url = url(self.hostname, self.port, "api_getWait")
		self.response = self.client.get(self.url)
		if self.response.status_code == 200:
			return False
		return True

	def getOutbox(self):
		self.url = url(self.hostname, self.port, "api_getOutbox")
		self.response = self.client.get(self.url)
		return json.loads(self.response.content)

	def getInbox(self):
		self.url = url(self.hostname, self.port, "api_getInbox")
		self.response = self.client.get(self.url)
		return json.loads(self.response.content)

	def getFolders(self):
		self.url = url(self.hostname, self.port, "api_getFolders")
		self.response = self.client.get(self.url)
		return json.loads(self.response.content)

	def getInFolder(self, folder_id):
		self.url = url(self.hostname, self.port, "api_getInFolder")
		self.post_data = dict(sessionid=self.sessionid, folder_id=folder_id, csrfmiddlewaretoken=self.csrftoken)
		self.response = self.client.post(self.url, self.post_data, cookies=self.cookies)
		return json.loads(self.response.content)

	def getAllMessages(self):
		self.url = url(self.hostname, self.port, "api_getAllMessages")
		self.response = self.client.get(self.url)
		return json.loads(self.response.content)

	def getReadedMessages(self):
		self.url = url(self.hostname, self.port, "api_getReadedMessages")
		self.response = self.client.get(self.url)
		return json.loads(self.response.content)

	def getUnreadedMessages(self):
		self.url = url(self.hostname, self.port, "api_getUnreadedMessages")
		self.response = self.client.get(self.url)
		return json.loads(self.response.content)

	def getState(self):
		self.url = url(self.hostname, self.port, "api_getState")
		self.response = self.client.get(self.url)
		return json.loads(self.response.content)

def getState(host):
	state = dict()
	state['inbox'] = host.getInbox()
	state['outbox'] = host.getOutbox()
	state['folders'] = host.getFolders()
	state['all'] = host.getAllMessages()
	state['readed'] = host.getReadedMessages()
	state['unreaded'] = host.getUnreadedMessages()
	for fol in state['folders']:
		state[fol] = host.getInFolder(fol)

	return state


if __name__ == '__main__':
	if len(sys.argv) != 2 and len(sys.argv) != 3 and len(sys.argv) != 4:
		print "[TEST] usage : python test_random.py parameter operation"		
		print "[TEST] parameter = -1 : register a test user"
		print "[TEST] parameter >= 0 : amount of operations"
		print "[TEST] if operation is not picked a test with random operation is starting"
		print "[TEST] optional operation in {0, 1, 2, 3, 4} with:"
		print "[TEST] \t 0 : add"
		print "[TEST] \t 1 : add_folder"
		print "[TEST] \t 2 : delete"
		print "[TEST] \t 3 : delete_folder"
		print "[TEST] \t 4 : change_folder"
		sys.exit(1)

	try:
		amount_op = int(sys.argv[1])
	except:
		print "[TEST] Pick a int as amount of operation."
		sys.exit(1)

	hst_list = []

	for host in ALL_HOSTS:
		try:
			client = Client(host['port'], host['hostname'])
			hst_list.append(client)
		except:
			print "[TEST] Host %s:%d is not online..." %  (host['hostname'], int(host['port']))
			sys.exit(1)

	print "[TEST] Register user on one host."
	hst_list[0].register('test_user', '1111', '1111')

	print "[TEST] Login user on each host.\n"
	for host in hst_list:
		while True:
			try:
				host.login('test_user', '1111')
				if host.response.status_code == 200:
					break
				else:
					pass
			except:
				time.sleep(1)
				pass

	time_result = 0
	count_result = [0, 0, 0, 0, 0, 0, 0]

	op = ['add', 'add_folder', 'delete', 'delete_folder', 'change_folder', 'mark_readed', 'mark_unreaded']

	count_fol = 0

	i = 0
	while i < amount_op:
		host = random.choice(hst_list)

		if i % 100 == 0:
			state = host.getState()
			count_fol = len(state['folders'])

		try:
			operation = int(sys.argv[2])
		except:
			rnd_list = []

			rnd_list.extend([0,0,0,0,0,0,0,0,0,0])
			rnd_list.extend([1])
			rnd_list.extend([2,2,2,2,2,2,2,2,2,2])
			rnd_list.extend([3])
			rnd_list.extend([4,4,4,4,4,4,4,4,4,4])
			rnd_list.extend([5,5,5,5,5,5,5,5,5,5])
			rnd_list.extend([6,6,6,6,6])

			operation = random.choice(rnd_list)


		# addMessage
		if operation == 0:
			op_start = time.time()
			host.addMessage(i)

		# addFolder
		if operation == 1:
			if count_fol >= 10:
				continue

			op_start = time.time()
			host.addFolder(i)
			count_fol += 1
			
		# deleteMessage
		if operation == 2:
			msg_list = state['all']

			if not msg_list:
				continue
			msg = random.choice(msg_list)

			op_start = time.time()
			host.deleteMessage(msg)

		# deleteFolder
		if operation == 3:
			if count_fol <= 5:
				continue

			fol_list = state['folders']

			if not fol_list:
				continue

			fol = random.choice(fol_list)

			op_start = time.time()
			host.deleteFolder(fol)
			count_fol -= 1

		# changeFolder
		if operation == 4:
			fol_list = list(state['folders'])

			if not fol_list:
				continue

			fol_list.append('Inbox')

			old_fol = random.choice(fol_list)
			new_fol = random.choice(fol_list)

			if old_fol == 'Inbox':
				msg_list = state['inbox']
			else:
				msg_list = state[old_fol]

			if not msg_list:
				continue

			msg = random.choice(msg_list)

			op_start = time.time()
			host.changeFolder(new_fol, old_fol, msg)

		# mark readed
		if operation == 5:
			msg_list = state['unreaded']

			if not msg_list:
				continue
			msg = random.choice(msg_list)

			op_start = time.time()
			host.mark_readed(msg)

		# mark readed
		if operation == 6:
			msg_list = state['readed']

			if not msg_list:
				continue
			msg = random.choice(msg_list)

			op_start = time.time()
			host.mark_unreaded(msg)

		if host.response.status_code != 200:
			print host.response.status_code
			continue

		op_end = time.time() - op_start
		op_time = json.loads(host.response.content)['time']

		with open("response.csv", "a") as f:
			f.write("%.7f\n" % op_end)

		with open("operation.csv", "a") as f:
			f.write("%.7f\n" % op_time)
		
		time_result += op_end
		print '[TEST] %.4f seconds : %s to %d' % (op_end, op[operation], int(host.port))
		count_result[operation] += 1

		if i >= 100 and i % (amount_op/(amount_op/100)) == 0:
			percent = int(float(i) / float(amount_op) * 100)
			print '\n[TEST] ' + str(percent) + ' %\tcompleted\n'

		i += 1

	if i != 0:
		percent = int(float(i) / float(amount_op) * 100)
		print '\n[TEST] ' + str(percent) + ' %\tcompleted\n'

		count = 0
		for c in count_result:
			count += c

		print "[TEST] " + str(count_result[0]) + " AddMessage operation."
		print "[TEST] " + str(count_result[1]) + " AddFolder operation."
		print "[TEST] " + str(count_result[2]) + " DeleteMessage operation."
		print "[TEST] " + str(count_result[3]) + " DeleteFolder operation."
		print "[TEST] " + str(count_result[4]) + " MoveMessage operation."
		print "[TEST] " + str(count_result[5]) + " ReadMessage operation."
		print "[TEST] " + str(count_result[6]) + " UnreadMessage operation."
		print "[TEST] makes " + str(count) + " operation.\n"

		print "[TEST] It took %.6f seconds (only the operation)." % time_result
		print "[TEST] It took %.6f seconds per operation (only the operation).\n" % float(time_result/count)

	start = time.time()
	x = 0
	while hst_list[0].getWait() or hst_list[1].getWait() or hst_list[2].getWait():
		if x == 100:
			print "[TEST] Waiting for hosts to converge.\n"
			x = 0
		else:
			x += 1
		pass

	if i != 0:
		print "[TEST] Wating for hosts to converge %.12f seconds." % (time.time() - start)
		print "[TEST] Wating for hosts to converge %.12f seconds per operation.\n" % float((time.time() - start)/count)			

	# Check states

	state_0 = getState(hst_list[0])
	state_1 = getState(hst_list[1])
	state_2 = getState(hst_list[2])

	all_len = 0

	if set(state_0['inbox']) == set(state_1['inbox']) == set(state_2['inbox']):
		all_len += len(state_0['inbox'])
		print '[TEST] Passed inbox check - got ' + str(len(state_0['inbox'])) + ' messages.'

	if set(state_0['outbox']) == set(state_1['outbox']) == set(state_2['outbox']):
		all_len += len(state_0['outbox'])
		print '[TEST] Passed outbox check - got ' + str(len(state_0['outbox'])) + ' messages.'

	if set(state_0['folders']) == set(state_1['folders']) == set(state_2['folders']):
		all_len += len(state_0['folders'])
		print '[TEST] Passed folder check - got ' + str(len(state_0['folders'])) + ' folders.'

		for fol in state_0['folders']:
			if set(state_0[fol]) == set(state_1[fol]) == set(state_2[fol]):
				all_len += len(state_0[fol])
				print '\t[TEST] Passed subcheck - got ' + str(len(state_0[fol])) + ' messages in folder.'
			else:
				print '\t[TEST] Not Passed subcheck!'

	print '[TEST] makes ' + str(all_len) + ' messages/folders.\n'

	if set(state_0['all']) == set(state_1['all']) == set(state_2['all']):
		print '[TEST] Passed check - got ' + str(len(state_0['all'])) + ' messages.'
		if set(state_0['readed']) == set(state_1['readed']) == set(state_2['readed']):
			print '[TEST] Passed readed check - got ' + str(len(state_0['readed'])) + "/" + str(len(state_0['all'])) + ' messages.'
		else:
			print '[TEST] Not Passed subcheck! - got ' + str(len(state_0['readed'])) + "/" + str(len(state_0['all'])) + ' messages.'
			print '[TEST] Not Passed subcheck! - got ' + str(len(state_1['readed'])) + "/" + str(len(state_0['all'])) + ' messages.'
			print '[TEST] Not Passed subcheck! - got ' + str(len(state_2['readed'])) + "/" + str(len(state_0['all'])) + ' messages.'

		if set(state_0['unreaded']) == set(state_1['unreaded']) == set(state_2['unreaded']):
			print '[TEST] Passed unreaded check - got ' + str(len(state_0['unreaded'])) + "/" + str(len(state_0['all'])) + ' messages.'
		else:
			print '[TEST] Not Passed subcheck! - got ' + str(len(state_0['unreaded'])) + "/" + str(len(state_0['all'])) + ' messages.'
			print '[TEST] Not Passed subcheck! - got ' + str(len(state_1['unreaded'])) + "/" + str(len(state_0['all'])) + ' messages.'
			print '[TEST] Not Passed subcheck! - got ' + str(len(state_2['unreaded'])) + "/" + str(len(state_0['all'])) + ' messages.'
	print "\n[TEST] Logout user on each host.\n"
	hst_list[0].logout()
	hst_list[1].logout()
	hst_list[2].logout()
