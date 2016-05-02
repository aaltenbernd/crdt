#!/usr/bin/env python
import os
import sys
import django



if __name__ == "__main__":

	# starting local host id = 0
	os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings.host_0")

	from django.core.management import execute_from_command_line

	execute_from_command_line(sys.argv)