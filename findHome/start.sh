#!/bin/bash

echo ""
echo "========================================"
echo "  IVG Real Estate Analyzer"
echo "  Avvio del server..."
echo "========================================"
echo ""

# Verifica se Python è installato
if ! command -v python3 &> /dev/null; then
    echo "ERRORE: Python non è installato!"
    echo "Installa Python con:"
    echo "  Mac: brew install python3"
    echo "  Linux: sudo apt install python3 python3-pip"
    exit 1
fi

# Verifica se le dipendenze sono installate
echo "Verifica dipendenze..."
if ! python3 -c "import flask" &> /dev/null; then
    echo "Installazione dipendenze..."
    pip3 install -r requirements.txt
fi

# Avvia il server
echo ""
echo "Server in avvio..."
echo "Apri il browser su: http://localhost:5000"
echo ""
echo "Premi CTRL+C per fermare il server"
echo ""

python3 app.py
