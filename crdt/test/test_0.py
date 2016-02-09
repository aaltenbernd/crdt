import requests
import time
import ast
import json
import logging

HOST = "http://127.0.0.1"
PORT = ["8000", "8001", "8002"]

OP = {}
OP['login'] = "api_login"
OP['logout'] = "api_logout"
OP['register'] = "api_register"
OP['addMessage'] = "api_addMessage"
OP['deleteMessage'] = "api_deleteMessage"
OP['addFolder'] = "api_addFolder"
OP['deleteFolder'] = "api_deleteFolder"
OP['changeFolder'] = "api_changeFolder"
OP['getCurrentState'] = "api_getCurrentState"
OP['getQueue'] = "api_getQueue"

def url(host, port, operation):
	return host + ":" + port + "/" + operation

class Test():
	def __init__(self, port):
		self.port = port
		self.username = None
		self.password = None
		self.text = "Test Message..."
		self.response = None
		self.sessionid = None

		self.client = requests.session()
		# only needed if csrf token is necessary
		self.url = "http://127.0.0.1:" + str(self.port)
		self.client.get(self.url)
		self.csrftoken = self.client.cookies['csrftoken']
		self.cookies = dict(self.client.cookies)

	def register(self, username, password, password_confirm):
		self.url = url(HOST, self.port, OP['register'])
		self.post_data = dict(username=username, password=password, password_confirm=password_confirm, csrfmiddlewaretoken=self.csrftoken)
		self.response = self.client.post(self.url, self.post_data, cookies=self.cookies)
		self.username = username
		self.password = password

	def login(self, username, password):
		self.url = url(HOST, self.port, OP['login'])
		self.post_data = dict(username=username, password=password, csrfmiddlewaretoken=self.csrftoken)
		self.response = self.client.post(self.url, self.post_data, cookies=self.cookies)
		self.sessionid = self.client.cookies['sessionid']
		self.csrftoken = self.client.cookies['csrftoken']
		self.cookies = dict(self.client.cookies)
		self.username = username
		self.password = password

	def logout(self):
		self.url = url(HOST, self.port, OP['logout'])
		self.response = self.client.get(self.url)

	def addMessage(self):
		self.url = url(HOST, self.port, OP['addMessage'])
		self.post_data = dict(sessionid=self.sessionid, text=self.text, reader=self.username, csrfmiddlewaretoken=self.csrftoken)
		self.response = self.client.post(self.url, self.post_data, cookies=self.cookies)

	def deleteMessage(self, uuid):
		self.url = url(HOST, self.port, OP['deleteMessage'])
		self.url = self.url + "/" + str(uuid) + "/"
		self.response = self.client.get(self.url)

	def getCurrentState(self):
		self.url = url(HOST, self.port, OP['getCurrentState'])
		self.response = self.client.get(self.url)

	def getQueue(self):
		self.url = url(HOST, self.port, OP['getQueue'])
		self.response = self.client.get(self.url)

	def addFolder(self, title):
		self.url = url(HOST, self.port, OP['addFolder'])
		self.post_data = dict(sessionid=self.sessionid, title=title, csrfmiddlewaretoken=self.csrftoken)
		self.response = self.client.post(self.url, self.post_data, cookies=self.cookies)

	def deleteFolder(self, uuid):
		self.url = url(HOST, self.port, OP['deleteFolder'])
		self.url = self.url + "/" + str(uuid) + "/"
		self.response = self.client.get(self.url)

	def changeFolder(self, folder_uuid, message_uuid):
		self.url = url(HOST, self.port, OP['changeFolder'])
		self.url = self.url + "/" + str(message_uuid) + "/"
		self.post_data = dict(sessionid=self.sessionid, folder_choice=folder_uuid, csrfmiddlewaretoken=self.csrftoken)
		self.response = self.client.post(self.url, self.post_data, cookies=self.cookies)

def add_messages(test, amount):
	print "[TEST] Adding " + str(amount) + " messages."
	print "[TEST] On host 127.0.0.1:" + str(test.port) + "."

	uuid = []

	start = time.time()
	
	for i in range(0, amount):
		test.addMessage()
		test_dict = json.loads(test.response.content)
		uuid.append(test_dict['uuid'])

	test.getQueue()

	test_dict = json.loads(test.response.content)

	while test_dict[test_dict.keys()[0]] > 0 or test_dict[test_dict.keys()[1]] > 0:
		test.getQueue()
		test_dict = json.loads(test.response.content)

	print "[TEST] It took " + str(time.time() - start) + " seconds.\n"

	return uuid

def delete_messages(test, uuid):
	print "[TEST] Deleting messages."
	print "[TEST] On host 127.0.0.1:" + str(test.port) + "."

	start = time.time()

	for message in uuid:
		test.deleteMessage(message)

	test.getQueue()

	test_dict = json.loads(test.response.content)

	while test_dict[test_dict.keys()[0]] > 0 or test_dict[test_dict.keys()[1]] > 0:
		test.getQueue()
		test_dict = json.loads(test.response.content)

	print "[TEST] It took " + str(time.time() - start) + " seconds.\n"

def add_folders(test, amount):

	folder_uuid = []

	print "[TEST] Adding " + str(amount) + " folders."
	print "[TEST] On host 127.0.0.1:" + str(test.port) + "."

	start = time.time()
	
	for i in range(0, amount):
		test.addFolder("test_folder")
		test_dict = json.loads(test.response.content)
		folder_uuid.append(test_dict['uuid'])

	test.getQueue()

	test_dict = json.loads(test.response.content)

	while test_dict[test_dict.keys()[0]] > 0 or test_dict[test_dict.keys()[1]] > 0:
		test.getQueue()
		test_dict = json.loads(test.response.content)

	print "[TEST] It took " + str(time.time() - start) + " seconds.\n"

	return folder_uuid

def change_folder_of_messages(test, folder, uuid):
	print "[TEST] Move messages to folder with id " + str(folder) + "."
	print "[TEST] On host 127.0.0.1:" + str(test.port) + "."

	start = time.time()

	for message in uuid:
		test.changeFolder(folder, message)
		test_dict = json.loads(test.response.content)

	test.getQueue()

	test_dict = json.loads(test.response.content)

	while test_dict[test_dict.keys()[0]] > 0 or test_dict[test_dict.keys()[1]] > 0:
		test.getQueue()
		test_dict = json.loads(test.response.content)

	print "[TEST] It took " + str(time.time() - start) + " seconds.\n"

def delete_folder(test, folder):
	print "[TEST] Delete folder with uuid " + str(folder) + "."
	print "[TEST] On host 127.0.0.1:" + str(test.port) + "."

	start = time.time()

	test.deleteFolder(folder)

	test.getQueue()

	test_dict = json.loads(test.response.content)

	while test_dict[test_dict.keys()[0]] > 0 or test_dict[test_dict.keys()[1]] > 0:
		test.getQueue()
		test_dict = json.loads(test.response.content)

	print "[TEST] It took " + str(time.time() - start) + " seconds.\n"

def print_state(test):
	test.getCurrentState()

	test_dict = json.loads(test.response.content)

	print "[TEST] State on 127.0.0.1:" + test.port + ":\n"

	print "\tMessage: " + str(test_dict['messages_count'])
	print "\tAddMessage: " + str(test_dict['add_messages_count'])
	print "\tDeleteMessage: " + str(test_dict['delete_messages_count']) + "\n"
	
	print "\tFolder: " + str(test_dict['folders_count'])
	for folder in test_dict['folder_dict'].iteritems():
		print "\t " + str(folder[0])[0:5] + " containing " + str(folder[1]) + " messages."
	print "\tAddFolder: " + str(test_dict['add_folder_count'])
	print "\tDeleteFolder: " + str(test_dict['delete_folder_count'])	
	print ""

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

	host_0_uuid = add_messages(test_0, 50)
	host_1_uuid = add_messages(test_1, 50)
	host_2_uuid = add_messages(test_2, 50)

	delete_messages(test_1, host_2_uuid)
	delete_messages(test_2, host_1_uuid)

	folder_uuid = add_folders(test_0, 5)

	list_0 = host_0_uuid[0:10]
	list_1 = host_0_uuid[10:20]
	list_2 = host_0_uuid[20:30]
	list_3 = host_0_uuid[30:40]
	list_4 = host_0_uuid[40:50]

	change_folder_of_messages(test_1, folder_uuid[0], list_0)
	change_folder_of_messages(test_2, folder_uuid[1], list_1)
	change_folder_of_messages(test_0, folder_uuid[2], list_2)
	change_folder_of_messages(test_1, folder_uuid[3], list_3)
	change_folder_of_messages(test_2, folder_uuid[4], list_4)

	delete_folder(test_0, folder_uuid[0])
	delete_folder(test_1, folder_uuid[1])
	delete_folder(test_2, folder_uuid[2])

	time.sleep(1)

	print_state(test_0)
	print_state(test_1)
	print_state(test_2)

	print "[TEST] Logout user on each host.\n"
	test_0.logout()
	test_1.logout()
	test_2.logout()