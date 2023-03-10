@echo OFF

set CONDAPATH=C:\ProgramData\Anaconda3

set ENVNAME=DavidEnv

rem call C:\ProgramData\Anaconda3\Scripts\activate.bat C:\ProgramData\Miniconda3
if %ENVNAME%==base (set ENVPATH=%CONDAPATH%) else (set ENVPATH=%CONDAPATH%\envs\%ENVNAME%)

call %CONDAPATH%\Scripts\activate.bat %ENVPATH%

set FLASK_APP=DavidTrader

set FLASK_ENV=development

flask run --host=0.0.0.0

start chrome http://localhost:5000

pause