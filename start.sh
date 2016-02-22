if [[ $1 == "--flush" ]]
	then
		python manage.py init --settings=settings.host_0
		python manage.py init --settings=settings.host_1
		python manage.py init --settings=settings.host_2
fi

screen -d -m python manage.py run_host --settings=settings.host_0
screen -r -X screen python manage.py run_host --settings=settings.host_1
screen -r -X screen python manage.py run_host --settings=settings.host_2
screen -r -X clear
screen -r