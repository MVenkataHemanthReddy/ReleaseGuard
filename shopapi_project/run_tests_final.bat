@echo off
cd /d "%~dp0"
call .venv\Scripts\python.exe manage.py test shop.tests -v 2