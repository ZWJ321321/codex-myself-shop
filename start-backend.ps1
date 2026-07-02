$env:MYSQL_PASSWORD = 'ttt321321'
Set-Location 'E:\餐厅介绍'
& 'E:\anaconda\python.exe' 'backend\manage.py' 'ensure_catalog_demo'
if ($LASTEXITCODE -ne 0) {
  exit $LASTEXITCODE
}
& 'E:\anaconda\python.exe' 'backend\manage.py' runserver '127.0.0.1:8000' '--noreload' *> 'backend-run.log'
