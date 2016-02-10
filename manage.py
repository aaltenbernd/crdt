#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":

	if sys.argv[2] == "8000":
		os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings.host_0")
	elif sys.argv[2] == "8001":
		os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings.host_1")
	elif sys.argv[2] == "8002":
		os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings.host_2")
	else:
		os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings.settings")

	from django.core.management import execute_from_command_line

	execute_from_command_line(sys.argv)