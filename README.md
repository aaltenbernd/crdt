### Bachelor-Thesis : Entwicklung eines verteilten Nachrichtensystems mit optimistischer Replikation

#### Anleitung zum Ausführen

##### Host hinzufügen/löschen:

###### Hinweis: 

Hosts können in der host_list Datei angepasst werden.
Neue Hosts müssen in Form eines Dictonary mit id und port des Hosts in der host_list hinzugefügt werden:

```
{'id': id, 'port': port}
```

Die standard Konfiguration ist für drei Server ausgelegt: 

```
{'id' : 0, 'port' : 8000}
{'id' : 1, 'port' : 8001}
{'id' : 2, 'port' : 8002}
```

##### Host mit id starten:

###### Hinweis: id muss in host_list vorkommen.

```
python manage.py start id
```