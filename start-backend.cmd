@echo off
set MYSQL_PASSWORD=ttt321321
"E:\anaconda\python.exe" backend\manage.py ensure_catalog_demo
if errorlevel 1 exit /b %errorlevel%
"E:\anaconda\python.exe" backend\manage.py runserver 127.0.0.1:8000 --noreload > backend-run.log 2> backend-error.log
