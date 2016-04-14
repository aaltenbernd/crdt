##### Distributed E-Mail Service Implemented With Conflict-Free Replicated Data Types

###### General



###### Develop : Getting started on localhost

On Ubuntu simply follow this instruction to deploy an instance of the E-Mail Service.

Install system packages:

```
sudo apt-get update && sudo apt-get upgrade
```

RUN sudo apt-get update && sudo apt-get upgrade
RUN sudo apt-get install postgresql postgresql-contrib
RUN sudo -u postgres psql -c "ALTER USER postgres PASSWORD ‚postgres‘;“
RUN sudo apt-get install python-pip python-psycopg2
RUN sudo pip install django
RUN sudo apt-get install git
RUN git clone https://github.com/aaltenbernd/crdt.git
RUN cd crdt/
RUN python manage.py makemigrations
RUN python manage.py migrate --settings=settings.aws_0


  



On Ubuntu simply follow this instruductions to deploy an instance.





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
