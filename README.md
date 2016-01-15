### Bachelor-Thesis : Entwicklung eines verteilten Nachrichtensystems mit optimistischer Replikation

#### Anleitung zum Ausführen

##### 

1. clone repository:
	```
	clone git clone https://github.com/aaltenbernd/crdt.git folder
	```
2. go to folder: 
	```
	cd folder
	```
3. configure host_list file:
	1. choose an id and a related port number for each server
	2. write id and port as dictonary {'id': choosen_id, 'port': choosen_port}
	3. write each server dictornary in one line of host_list file
	4. example:
	```
	{'id' : 0, 'port' : 8000}
	{'id' : 1, 'port' : 8001}
	{'id' : 2, 'port' : 8002}
	```
4. start server with choosen id:
	```
	python manage.py start ID
	```