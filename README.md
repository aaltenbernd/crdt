##### Distributed E-Mail Service Implemented With Conflict-Free Replicated Data Types

###### Develop : General

Generally each host has a id, port and hostname. Further each host a settings file located in ```settings/host_ID```. The hostlist is given in line 19-23:
```python
ALL_HOSTS = [
	{'id' : 0, 'port' : 8000, 'hostname' : "http://127.0.0.1"},
	{'id' : 1, 'port' : 8001, 'hostname' : "http://127.0.0.1"},
	{'id' : 2, 'port' : 8002, 'hostname' : "http://127.0.0.1"},
]
``` 

* each host has a id, port and hostname
* each host has a settings file in ```settings/host_ID```
* on default:





###### Develop : Getting started on localhost

On Ubuntu simply follow this instruction to deploy an instance of the E-Mail Service.

Install postgres, by:

```
sudo apt-get install postgresql postgresql-contrib
```
In a terminal, type:

```
sudo -u postgres psql postgres
```
Set "postgres" as a password for the "postgres" database role using the command. Afterwards type Control+D or \q to exit the posgreSQL prompt:

```
\postgres postgres
```
To create the database, type:

```
sudo -u postgres createdb db_host_ID
```

Install system packages:

```
sudo apt-get install python-pip python-psycopg2
```
Get the django framework with pip:

```
sudo pip install django
```
Finally, clone the repository:

```
git clone https://github.com/aaltenbernd/crdt.git
```
Make migrations, by:

```
python crdt/manage.py makemigrations
```
And migrate these to the database:

```
python crdt/manage.py migrate --settings=settings.host_ID
```
Start the instance, by:

```
python crdt/manage.py run_host --settings=settings.host_ID
```
If you want to clear the database, type:

```
python crdt/manage.py init --settings=settings.host_ID
```




* Jeder Host ist als Paar mit ID und PORT gespeichert
* Die Standardkonfiguration hat drei Hosts:
	* ```ID = 0 und PORT = 8000```
	* ```ID = 1 und PORT = 8001```
	* ```ID = 2 und PORT = 8002```
* Hosts können mit Angabe des jeweiligen ports gestrartet werden.
* Postgres Datenbank ist auf ```127.0.0.1:5432``` gesetzt
* jeweilige Datenbank muss als ```db_host_ID``` benannt sein

###### Host starten:

```
python manage.py run_host --settings=settings.host_ID
```

###### Host zurücksetzen:

```
python manage.py init --settings=settings.host_ID
```
