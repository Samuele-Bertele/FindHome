# 🚀 GUIDA RAPIDA - AVVIO IMMEDIATO

## Windows

1. **Installa Python** (se non lo hai già):
   - Vai su https://www.python.org/downloads/
   - Scarica l'ultima versione
   - Durante l'installazione, **seleziona "Add Python to PATH"**

2. **Avvia l'applicazione**:
   - Fai doppio clic su `start.bat`
   - Oppure apri il prompt dei comandi e digita: `start.bat`

3. **Apri il browser**:
   - Vai su http://localhost:5000

## Mac / Linux

1. **Installa Python** (se non lo hai già):
   ```bash
   # Mac
   brew install python3
   
   # Linux (Ubuntu/Debian)
   sudo apt install python3 python3-pip
   ```

2. **Avvia l'applicazione**:
   ```bash
   ./start.sh
   ```
   
   Se non funziona, dai i permessi:
   ```bash
   chmod +x start.sh
   ./start.sh
   ```

3. **Apri il browser**:
   - Vai su http://localhost:5000

## ⚡ Avvio Manuale

Se gli script non funzionano, usa questi comandi:

```bash
# 1. Installa le dipendenze (solo la prima volta)
pip install -r requirements.txt

# 2. Avvia il server
python app.py

# 3. Apri il browser su http://localhost:5000
```

## 🎯 Primo Utilizzo

1. Inserisci i filtri di ricerca:
   - Prezzo massimo (es. 150000)
   - Metri quadri minimi (es. 80)
   - Zona geografica (es. "Reggio Emilia")

2. Clicca su "Analizza Immobili"

3. Attendi il caricamento (può richiedere 10-30 secondi)

4. Visualizza i risultati e clicca su "Vedi offerta su IVG" per aprire la pagina originale

## ❓ Problemi?

### Il server non si avvia
- Verifica che Python sia installato: `python --version`
- Installa le dipendenze: `pip install -r requirements.txt`

### Nessun risultato
- Verifica la connessione internet
- Prova con filtri meno restrittivi
- Il sito IVG potrebbe essere temporaneamente non disponibile

### Errore "Porta già in uso"
- Chiudi altre applicazioni che usano la porta 5000
- Oppure modifica la porta in `app.py`

## 📱 Contatti

Per il README completo, consulta `README.md`

---

**Divertiti con la ricerca! 🏠**
