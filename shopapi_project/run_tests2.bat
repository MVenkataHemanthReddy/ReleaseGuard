@echo off
cd /d "D:\Release Guard\shopapi_project"
.venv\Scripts\python.exe manage.py test shop.tests -v 2
pause