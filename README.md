Bachelor-Thesis : Entwicklung eines verteilten Nachrichtensystems mit optimistischer Replikation

Anleitung zum Testen : 

1 - Repository in zwei unterschiedlichen Verzeichnissen klonen
	- git clone https://github.com/aaltenbernd/crdt.git
2 - Zwei Ports aussuchen
	- PORT_A = 8000
	- PORT_B = 9000
3 - Server initialisieren und starten (hier für Server_A)
	- python manage.py makemigrations
	- python manage.py migrate
	- python manage.py shell
		- from crdt.models import Node
		- Node.objects.create(port=PORT_B)
		- exit()
	- python manage.py runserver localHost:PORT_A
4 - Jeweils Empfänger/Sender Prozess starten
	- python manage.py broadcast
	- Schickt Operation (Add, Increment, Decrement) an den anderen Server (per HTTP)
	- Empfängt Operation und führt diese aus
5 - Beide Server im browser aufrufen:
	- http://localHost:PORT_A
	- http://localHost:PORT_B 
6 - Funktionen testen : 
	- Add : Fügt Nummer hinzu 
	- + / - : inkrementiert / dekrementiert die Nummer 
	- Delete All : Löscht alle Nummern
		- Nur zum Reset gedacht (wird nicht verteilt)