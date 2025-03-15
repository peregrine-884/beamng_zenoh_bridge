@echo off
echo Activating Python virtual environment...
call ..\venv\Scripts\activate

cd ..\tasks\autoware_drive
python main.py

