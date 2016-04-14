### Distributed E-Mail-Service Implemented With CRDTs

#### Localhost : General 

Generally each host has an **id**, a **port** and a **hostname**. Further there is a settings file located in ```settings/host_ID``` for each host. By default ```python manage.py runserver``` will start the server with the ```settings/host_0``` file. The initial setup includes three hosts.

* The hostlist is given in line 19-23:

```python
ALL_HOSTS = [
	{'id' : 0, 'port' : 8000, 'hostname' : "http://127.0.0.1"},
	{'id' : 1, 'port' : 8001, 'hostname' : "http://127.0.0.1"},
	{'id' : 2, 'port' : 8002, 'hostname' : "http://127.0.0.1"},
]
```

* And the running host is specified in line 25:

```python
RUNNING_HOST = ALL_HOSTS[ID]
```

* The connection to the postgres database can be configured in line 6-15:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'db_host_ID',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

#### Localhost : Getting started

On Ubuntu simply follow this instruction to deploy an instance of the E-Mail-Service.

Install postgres, by:

```
sudo apt-get install postgresql postgresql-contrib
```
In a terminal, type:

```
sudo -u postgres psql postgres
```
Set "postgres" as a password for the "postgres" database role using the command:

```
\postgres postgres
```
Type Control+D or \q to exit the posgreSQL prompt.

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

#### Develop on different hosts

On Ubuntu simply follow the instruction ahead on each host.

Afterwards configure the hostlist in the ```settings/host_ID``` file and manipulate the IPs: 

```python
ALL_HOSTS = [
	{'id' : 0, 'port' : 8000, 'hostname' : "http://IP_HOST_0"},
	{'id' : 1, 'port' : 8001, 'hostname' : "http://IP_HOST_1"},
	{'id' : 2, 'port' : 8002, 'hostname' : "http://IP_HOST_2"},
]
```
And start the host, by:

```
python crdt/manage.py run_host --settings=settings.host_ID --production
```


#### Test

Start a simple test, by:

```
python crdt/crdt/test/test_random.py
```

If the E-Mail-Service is developed on different hosts, also configure the host list in line 14-18 and start the test, by:
```
ENV=production python crdt/crdt/test/test_random.py
```

