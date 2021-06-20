@echo off
title    START SYNC E and Jira
set str=...........Start..at..
set str_e=...........End  ..at..
echo  %str% %DATE% %TIME%
echo.
echo/
rem dir *.py *.exe
python Main.py || echo  not success
rem echo %errorlevel%

rem type EJmap.py


rem :label 
rem date/t & time/t
rem echo+
rem date/t && time/t
rem tree
echo.
echo %str_e% %DATE% %TIME%
rem start ls
::goto label
::cls
::ver
::vol

pause