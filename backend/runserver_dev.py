import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
os.environ['MYSQL_PASSWORD'] = 'ttt321321'

from django.core.management import execute_from_command_line

execute_from_command_line(['backend/manage.py', 'runserver', '127.0.0.1:8000', '--noreload'])
