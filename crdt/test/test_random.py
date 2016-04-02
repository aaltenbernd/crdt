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
				break
			except:
				time.sleep(1)
				pass

	time_result = 0
	count_result = [0, 0, 0, 0, 0, 0, 0]

	op = ['add', 'add_folder', 'delete', 'delete_folder', 'change_folder', 'mark_readed', 'mark_unreaded']

	i = 0
	while i < amount_op:
		host = random.choice(hst_list)

		if i % 100 == 0:
			print "[TEST] Get state...\n"
			state = getState(host)

		try:
			operation = int(sys.argv[2])
		except:
			#data['number']+1
			operation = random.choice([
							0,0,0,0,0,0,0,0,0,0,
							#1,1,
							2,2,2,2,2,
							#3,
							4,4,4,4,4,4,4,4,4,4,
							5,5,5,5,5,5,5,5,5,5,
							6,6,6,6,6])

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
			msg_list = state['all']

			if not msg_list:
				continue
			msg = random.choice(msg_list)

			op_start = time.time()
			host.deleteMessage(msg)

		# deleteFolder
		if operation == 3:
			fol_list = state['folders']

			if not fol_list:
				continue

			fol = random.choice(fol_list)

			op_start = time.time()
			host.deleteFolder(fol)

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

		#op_end = time.time() - op_start
		op_end = json.loads(host.response.content)['time']
		time_result += op_end
		print '[TEST] %.4f seconds : %s to %d' % (op_end, op[operation], int(host.port))
		count_result[operation] += 1

		if i >= 10 and i % (amount_op/(amount_op/10)) == 0:
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

	inbox_0 = set(hst_list[0].getInbox())
	outbox_0 = set(hst_list[0].getOutbox())
	folders_0 = set(hst_list[0].getFolders())
	all_0 = set(hst_list[0].getAllMessages())
	readed_0 = set(hst_list[0].getReadedMessages())
	unreaded_0 = set(hst_list[0].getUnreadedMessages())

	inbox_1 = set(hst_list[1].getInbox())
	outbox_1 = set(hst_list[1].getOutbox())
	folders_1 = set(hst_list[1].getFolders())
	all_1 = set(hst_list[1].getAllMessages())
	readed_1 = set(hst_list[1].getReadedMessages())
	unreaded_1 = set(hst_list[1].getUnreadedMessages())

	inbox_2 = set(hst_list[2].getInbox())
	outbox_2 = set(hst_list[2].getOutbox())
	folders_2 = set(hst_list[2].getFolders())
	all_2 = set(hst_list[2].getAllMessages())
	readed_2 = set(hst_list[2].getReadedMessages())
	unreaded_2 = set(hst_list[2].getUnreadedMessages())

	all_len = 0

	if inbox_0 == inbox_1 == inbox_2:
		all_len += len(inbox_0)
		print '[TEST] Passed inbox check - got ' + str(len(inbox_0)) + ' messages.'

	if outbox_0 == outbox_1 == outbox_2:
		all_len += len(outbox_0)
		print '[TEST] Passed outbox check - got ' + str(len(outbox_0)) + ' messages.'

	if folders_0 == folders_1 == folders_2:
		all_len += len(folders_0)
		print '[TEST] Passed folder check - got ' + str(len(folders_0)) + ' folders.'

		for fol in folders_0:
			in_fol_0 = set(hst_list[0].getInFolder(fol))
			in_fol_1 = set(hst_list[1].getInFolder(fol))
			in_fol_2 = set(hst_list[2].getInFolder(fol))
			if in_fol_0 == in_fol_1 == in_fol_2:
				all_len += len(in_fol_0)
				print '\t[TEST] Passed subcheck - got ' + str(len(in_fol_0)) + ' messages in folder.'
			else:
				print '\t[TEST] Not Passed subcheck!'

	print '[TEST] makes ' + str(all_len) + ' messages/folders.\n'

	if all_0 == all_1 == all_2:
		print '[TEST] Passed check - got ' + str(len(all_0)) + ' messages.'
		if readed_0 == readed_1 == readed_2:
			print '[TEST] Passed readed check - got ' + str(len(readed_0)) + "/" + str(len(all_0)) + ' messages.'

		if unreaded_0 == unreaded_1 == unreaded_2:
			print '[TEST] Passed unreaded check - got ' + str(len(unreaded_0)) + "/" + str(len(all_0)) + ' messages.'

	print "\n[TEST] Logout user on each host.\n"
	hst_list[0].logout()
	hst_list[1].logout()
	hst_list[2].logout()