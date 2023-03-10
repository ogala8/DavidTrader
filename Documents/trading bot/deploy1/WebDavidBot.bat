@echo OFF


set CONDAPATH=C:\Users\ADM-LABO-947501\Anaconda3

set ENVNAME=davidenv

rem call C:\ProgramData\Anaconda3\Scripts\activate.bat C:\ProgramData\Miniconda3
if %ENVNAME%==base (set ENVPATH=%CONDAPATH%) else (set ENVPATH=%CONDAPATH%\envs\%ENVNAME%)

call %CONDAPATH%\Scripts\activate.bat %ENVPATH%

set FLASK_APP=DavidTrader

set FLASK_ENV=development

START /B flask run --host=0.0.0.0

start firefox http://localhost:5000

pause