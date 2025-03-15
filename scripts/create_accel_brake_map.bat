@echo off
echo Activating Python virtual environment...
call ..\venv\Scripts\activate

cd ..\tasks\accel_brake_map
python main.py

