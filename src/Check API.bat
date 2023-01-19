@echo off
title Check API
call env/Scripts/activate
python test_api.py
pause > nul