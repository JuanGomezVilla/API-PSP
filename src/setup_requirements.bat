@echo off
title Installing requirements 
call .\env\Scripts\activate.bat
echo Activating virtual environment...
pip install -r requirements.txt
echo. 
echo Command done, you can close the window
pause > nul