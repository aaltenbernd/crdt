##### Bachelor-Thesis : Entwicklung eines verteilten Nachrichtensystems mit optimistischer Replikation

###### Allgemeines:

* Jeder Host ist als Paar mit ID und PORT gespeichert
* Die Standardkonfiguration hat drei Hosts:
	* ```ID = 0 und PORT = 8000```
	* ```ID = 1 und PORT = 8001```
	* ```ID = 2 und PORT = 8002```
* Hosts können mit Angabe des jeweiligen ports gestrartet werden.
* Postgres Datenbank ist auf ```127.0.0.1:5432``` gestetzt
* jeweilige Datenbank muss als ```db_host_ID``` benannt sein

###### Host starten:

```
python manage.py run_host --settings=settings.host_ID
```

###### Host zurücksetzen:

```
python manage.py init --settings=settings.host_ID
```
