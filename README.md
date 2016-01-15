##### Bachelor-Thesis : Entwicklung eines verteilten Nachrichtensystems mit optimistischer Replikation

###### Allgemeines:

* Jeder Host ist als Paar mit ID und PORT gespeichert
* Die Standardkonfiguration hat drei Hosts (siehe host_list):
	* ID = 0 und PORT = 8000
	* ID = 1 und PORT = 8001
	* ID = 2 und PORT = 8002
* Hosts können mit Angabe der ID (und PORT) gestartet, hinzugefügt und gelöscht werden

###### Host start:

```
python manage.py start_host ID
```

###### Host hinzufügen:

```
python manage.py add_host ID PORT
```

###### Host löschen:

```
python manage.py delete_host ID
```

