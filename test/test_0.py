import requests
import time
import ast
import json

HOST = "http://127.0.0.1"
PORT = ["8000", "8001", "8002"]

OP = {}
OP['login'] = "api_login"
OP['logout'] = "api_logout"
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
		self.username = "test_user"
		self.password = "1111"
		self.text = "Test Message..."
		self.post_data = dict(username=self.username, password=self.password)
		self.url = url(HOST, self.port, OP['login'])

		self.client = requests.session()
		# only needed if csrf token is necessary
		# self.client.get(self.url)
		# self.csrftoken = self.client.cookies
		
		self.response = self.client.post(self.url, self.post_data)
		self.sessionid = self.client.cookies['sessionid']

	def addMessage(self):
		self.url = url(HOST, self.port, OP['addMessage'])
		self.post_data = dict(sessionid=self.sessionid, text=self.text, reader=self.username)
		self.response = self.client.post(self.url, self.post_data)

	def deleteMessage(self, uuid):
		self.url = url(HOST, self.port, OP['deleteMessage'])
		self.url = self.url + "/" + uuid + "/"
		self.response = self.client.port(self.url)

	def getCurrentState(self):
		self.url = url(HOST, self.port, OP['getCurrentState'])
		self.response = self.client.get(self.url)

	def getQueue(self):
		self.url = url(HOST, self.port, OP['getQueue'])
		self.response = self.client.get(self.url)

if __name__ == '__main__':
	test_0 = Test(PORT[0])
	test_1 = Test(PORT[1])
	test_2 = Test(PORT[2])

	print ">>> Adding 1000 messages to one Host."

	start = time.clock()
	
	for i in range(0,1000):
		test_0.addMessage()

	test_0.getQueue()

	test_0_dict = json.loads(test_0.response.content)

	while test_0_dict["1"] > 0 or test_0_dict["2"] > 0:
		test_0.getQueue()
		test_0_dict = json.loads(test_0.response.content)


	print ">>> It took " + str(time.clock() - start) + " sec"

	print ">>> Adding 1000 messages alternately to each Host."

	start = time.clock()

	c = 0
	for i in range(0,1000):
		if c == 0:
			test_0.addMessage()
			c = 1
		elif c == 1:
			test_1.addMessage()
			c = 2
		elif c == 2:
			test_2.addMessage()
			c = 0

	test_0.getQueue()
	test_0_dict = json.loads(test_0.response.content)
	test_1.getQueue()
	test_1_dict = json.loads(test_1.response.content)
	test_2.getQueue()
	test_2_dict = json.loads(test_2.response.content)

	while test_0_dict["1"] > 0 or test_0_dict["2"] > 0 or test_1_dict["0"] > 0 or test_1_dict["2"] > 0 or test_2_dict["0"] > 0 or test_2_dict["1"] > 0:
		test_0.getQueue()
		test_0_dict = json.loads(test_0.response.content)
		test_1.getQueue()
		test_1_dict = json.loads(test_1.response.content)
		test_2.getQueue()
		test_2_dict = json.loads(test_2.response.content)

	print ">>> It took " + str(time.clock() - start) + " sec"

	test_0.getCurrentState()
	test_1.getCurrentState()
	test_2.getCurrentState()

	test_0_dict = json.loads(test_0.response.content)
	test_1_dict = json.loads(test_1.response.content)
	test_2_dict = json.loads(test_2.response.content)

	print "State on 127.0.0.1:8000:"
	print "------------------------"
	print "AddMessage: " + str(test_0_dict['add_messages_count'])
	print "DeleteMessage: " + str(test_0_dict['delete_messages_count'])
	print "Message: " + str(test_0_dict['messages_count'])
	print ""

	print "State on 127.0.0.1:8001:"
	print "------------------------"
	print "AddMessage: " + str(test_1_dict['add_messages_count'])
	print "DeleteMessage: " + str(test_1_dict['delete_messages_count'])
	print "Message: " + str(test_1_dict['messages_count'])
	print ""

	print "State on 127.0.0.1:8002:"
	print "------------------------"
	print "AddMessage: " + str(test_2_dict['add_messages_count'])
	print "DeleteMessage: " + str(test_2_dict['delete_messages_count'])
	print "Message: " + str(test_2_dict['messages_count'])
	print ""
	


