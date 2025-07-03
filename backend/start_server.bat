@echo off
echo Starting Word Cloud Generator API...
echo.

REM Set production environment variables
set FLASK_ENV=production
set DEBUG=0

REM Start the server using waitress
python -m waitress --port=8000 app:app

pause 