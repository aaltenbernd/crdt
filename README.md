##### Bachelor-Thesis : Entwicklung eines verteilten Nachrichtensystems mit optimistischer Replikation

###### Allgemeines:

* Jeder Host ist als Paar mit ID und PORT gespeichert
* Die Standardkonfiguration hat drei Hosts:
	* ID = 0 und PORT = 8000
	* ID = 1 und PORT = 8001
	* ID = 2 und PORT = 8002
* Hosts können mit Angabe der jeweiligen Settings-Datei gestartet. (host_0.py, host_1.py und host_2.py)

###### Host starten:

```
python manage.py run_host --settings=host_ID
```

