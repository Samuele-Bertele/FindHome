@echo off
echo.
echo ========================================
echo   IVG Real Estate Analyzer
echo   Avvio del server...
echo ========================================
echo.

REM Verifica se Python è installato
python --version >nul 2>&1
if errorlevel 1 (
    echo ERRORE: Python non e' installato!
    echo Scarica Python da: https://www.python.org/downloads/
    echo Durante l'installazione, seleziona "Add Python to PATH"
    pause
    exit /b 1
)

REM Verifica se le dipendenze sono installate
echo Verifica dipendenze...
pip show flask >nul 2>&1
if errorlevel 1 (
    echo Installazione dipendenze...
    pip install -r requirements.txt
)

REM Avvia il server
echo.
echo Server in avvio...
echo Apri il browser su: http://localhost:5000
echo.
echo Premi CTRL+C per fermare il server
echo.
python app.py

pause
