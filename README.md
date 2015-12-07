Bachelor-Thesis : Entwicklung eines verteilten Nachrichtensystems mit optimistischer Replikation

Anleitung zum Testen : 

1 - Repository in zwei unterschiedlichen Verzeichnissen klonen
	- git clone https://github.com/aaltenbernd/crdt.git
2 - Zwei Ports aussuchen
	- PORT_A = 8000
	- PORT_B = 9000
3 - Server initialisieren und starten (hier f�r Server_A)
	- python manage.py makemigrations
	- python manage.py migrate
	- python manage.py shell
		- from crdt.models import Node
		- Node.objects.create(port=PORT_B)
		- exit()
	- python manage.py runserver localHost:PORT_A
4 - Jeweils Empf�nger/Sender Prozess starten
	- python manage.py broadcast
	- Schickt Operation (Add, Increment, Decrement) an den anderen Server (per HTTP)
	- Empf�ngt Operation und f�hrt diese aus
5 - Beide Server im browser aufrufen:
	- http://localHost:PORT_A
	- http://localHost:PORT_B 
6 - Funktionen testen : 
	- Add : F�gt Nummer hinzu 
	- + / - : inkrementiert / dekrementiert die Nummer 
	- Delete All : L�scht alle Nummern
		- Nur zum Reset gedacht (wird nicht verteilt)