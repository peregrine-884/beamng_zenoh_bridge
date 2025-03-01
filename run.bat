@echo off
echo Activating Python virtual environment...
call .\venv\Scripts\activate

echo Starting Python script...
set SCENARIO_NUM=%1
set TIME_ZONE=%2
if "%TIME_ZONE%"=="" (
  set TIME_ZONE=afternoon
)
echo Scenario number: %SCENARIO_NUM%
echo Time zone: %TIME_ZONE%

cd .\beamng\
python main.py %SCENARIO_NUM% %TIME_ZONE%

