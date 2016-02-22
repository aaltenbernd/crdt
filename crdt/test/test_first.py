import requests
import time
import ast
import json
import logging

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

def add_messages(test, amount):
	print "[TEST] Adding " + str(amount) + " messages. (x2 outbox)"
	print "[TEST] On host 127.0.0.1:" + str(test.port) + "."

	uuid = []

	start = time.time()
	
	for i in range(0, amount):
		test.addMessage(i)
		test_dict = json.loads(test.response.content)
		uuid.append(test_dict['uuid'])

	print "[TEST] Send... Waiting for host"

	while test.waitForHost():
		pass

	end = time.time() - start

	print "[TEST] It took " + str(end) + " seconds.\n"

	return uuid

def delete_messages(test, uuid):
	print "[TEST] Deleting messages."
	print "[TEST] On host 127.0.0.1:" + str(test.port) + "."

	start = time.time()

	for message in uuid:
		test.deleteMessage(message)

	while test.waitForHost():
		pass

	end = time.time() - start

	print "[TEST] It took " + str(end) + " seconds.\n"

def add_folders(test, amount):

	folder_uuid = []

	print "[TEST] Adding " + str(amount) + " folders."
	print "[TEST] On host 127.0.0.1:" + str(test.port) + "."

	start = time.time()
	
	for i in range(0, amount):
		test.addFolder(i)
		test_dict = json.loads(test.response.content)
		folder_uuid.append(test_dict['uuid'])

	while test.waitForHost():
		pass

	end = time.time() - start

	print "[TEST] It took " + str(end) + " seconds.\n"

	return folder_uuid

def change_folder_of_messages(test, folder, uuid):
	print "[TEST] Move messages to folder with id " + str(folder) + "."
	print "[TEST] On host 127.0.0.1:" + str(test.port) + "."

	start = time.time()

	for message in uuid:
		test.changeFolder(folder, message)
		test_dict = json.loads(test.response.content)

	while test.waitForHost():
		pass

	end = time.time() - start

	print "[TEST] It took " + str(end) + " seconds.\n"

def delete_folder(test, folder):
	print "[TEST] Delete folder with uuid " + str(folder) + "."
	print "[TEST] On host 127.0.0.1:" + str(test.port) + "."

	start = time.time()

	test.deleteFolder(folder)

	while test.waitForHost():
		pass

	end = time.time() - start

	print "[TEST] It took " + str(end) + " seconds.\n"

if __name__ == '__main__':
	print "[TEST] Starting crdt mail service test.\n"

	test_0 = Test(PORT[0])
	test_1 = Test(PORT[1])
	test_2 = Test(PORT[2])

	print "[TEST] Register user on one host."
	test_0.register('test_user', '1111', '1111')

	time.sleep(3)

	print "[TEST] Login user on each host.\n"
	test_0.login('test_user', '1111')
	test_1.login('test_user', '1111')
	test_2.login('test_user', '1111')	

	host_0_uuid = add_messages(test_0, 100)
	host_1_uuid = add_messages(test_1, 100)
	host_2_uuid = add_messages(test_2, 100)

	delete_messages(test_1, host_2_uuid)
	delete_messages(test_2, host_1_uuid)

	folder_uuid = add_folders(test_0, 5)

	list_0 = host_0_uuid[0:20]
	list_1 = host_0_uuid[20:40]
	list_2 = host_0_uuid[40:60]
	list_3 = host_0_uuid[60:80]
	list_4 = host_0_uuid[80:100]

	change_folder_of_messages(test_1, folder_uuid[0], list_0)
	change_folder_of_messages(test_2, folder_uuid[1], list_1)
	change_folder_of_messages(test_0, folder_uuid[2], list_2)
	change_folder_of_messages(test_1, folder_uuid[3], list_3)
	change_folder_of_messages(test_2, folder_uuid[4], list_4)

	delete_folder(test_0, folder_uuid[0])
	delete_folder(test_1, folder_uuid[1])
	delete_folder(test_2, folder_uuid[2])

	time.sleep(2)

	state_0 = test_0.getState()
	add_msg_set_0 = set()
	for msg in state_0['add_messages']:
		add_msg_set_0.add((msg[0], msg[1]))
	del_msg_set_0 = set(json.loads(test_0.response.content)['delete_messages'])
	add_fol_set_0 = set(json.loads(test_0.response.content)['add_folders'])
	del_fol_set_0 = set(json.loads(test_0.response.content)['delete_folders'])

	state_1 = test_1.getState()
	add_msg_set_1 = set()
	for msg in state_1['add_messages']:
		add_msg_set_1.add((msg[0], msg[1]))
	del_msg_set_1 = set(json.loads(test_1.response.content)['delete_messages'])
	add_fol_set_1 = set(json.loads(test_1.response.content)['add_folders'])
	del_fol_set_1 = set(json.loads(test_1.response.content)['delete_folders'])

	state_2 = test_2.getState()
	add_msg_set_2 = set()
	for msg in state_2['add_messages']:
		add_msg_set_2.add((msg[0], msg[1]))
	del_msg_set_2 = set(json.loads(test_2.response.content)['delete_messages'])
	add_fol_set_2 = set(json.loads(test_2.response.content)['add_folders'])
	del_fol_set_2 = set(json.loads(test_2.response.content)['delete_folders'])

	if add_msg_set_0 == add_msg_set_1 == add_msg_set_2:
		print '[TEST] Passed addMessage check - got ' + str(len(add_msg_set_0)) + ' addMessage.'

	if del_msg_set_0 == del_msg_set_1 == del_msg_set_2:
		print '[TEST] Passed delMessage check - got ' + str(len(del_msg_set_0)) + ' delMessage.'

	if add_fol_set_0 == add_fol_set_1 == add_fol_set_2:
		print '[TEST] Passed addFolder check - got ' + str(len(add_fol_set_0)) + ' addFolder.'

	if del_fol_set_0 == del_fol_set_1 == del_fol_set_2:
		print '[TEST] Passed delFolder check - got ' + str(len(del_fol_set_0)) + ' delFolder.'

	all_len = len(add_msg_set_0) + len(del_msg_set_0) + len(add_fol_set_0) + len(del_fol_set_0)

	print '[TEST] makes ' + str(all_len) + 'saves.'


	print "[TEST] Logout user on each host.\n"
	test_0.logout()
	test_1.logout()
	test_2.logout()
