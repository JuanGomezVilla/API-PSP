@echo off
title FlaskDebugger
call env/scripts/activate
flask --app application.py --debug run