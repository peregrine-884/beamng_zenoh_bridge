@echo off
echo Activating Python virtual environment...
call ..\venv\Scripts\activate

cd ..\tasks\pointcloud_map
python main.py

