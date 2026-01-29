# 🏛️ Analizzatore Immobili IVG - Real Estate Analyzer

Sistema completo per l'analisi automatica degli immobili dalle aste giudiziarie con web scraping intelligente e fallback automatico.

## 📋 Caratteristiche

- ✅ **Web Scraping Multi-Source**: Prova automaticamente diversi portali di aste
- 🎯 **Filtri Avanzati**: prezzo, superficie, località
- 📊 **Sistema di Matching Intelligente**: calcola la corrispondenza ai tuoi criteri
- 🎨 **Interfaccia Moderna e Responsive**
- 🔗 **Link Diretti** alle offerte sui siti ufficiali
- ⚡ **API REST** per integrazioni future
- 🔄 **Fallback Automatico**: usa dati di esempio se il scraping non funziona

## 🚀 Installazione Rapida

### Requisiti

- Python 3.8 o superiore
- Connessione internet

### Passo 1: Installare Python

**Windows:**
1. Scarica Python da [python.org](https://www.python.org/downloads/)
2. Durante l'installazione, **seleziona "Add Python to PATH"**

**Mac:**
```bash
# Usando Homebrew
brew install python3
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3 python3-pip
```

### Passo 2: Installare le Dipendenze

Apri il terminale/prompt dei comandi nella cartella del progetto ed esegui:

```bash
pip install -r requirements.txt
```

Oppure installa manualmente:

```bash
pip install requests beautifulsoup4 flask lxml
```

### Passo 3: Avviare l'Applicazione

**Windows:**
```bash
# Doppio clic su start.bat
# OPPURE
python app.py
```

**Mac/Linux:**
```bash
./start.sh
# OPPURE  
python3 app.py
```

Vedrai un messaggio simile a questo:

```
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║        🏛️  IVG Real Estate Analyzer API Server          ║
    ║                                                           ║
    ║  Server attivo su: http://localhost:5000                 ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
```

### Passo 4: Aprire l'Applicazione

Apri il browser e vai su: **http://localhost:5000**

## 📖 Come Funziona

### Sistema di Web Scraping Intelligente

L'applicazione tenta di estrarre dati reali da vari portali di aste giudiziarie:

1. **astagiudiziaria.com** - Portale ufficiale IVG
2. **astegiudiziarie.it** - Aste Giudiziarie Inlinea
3. **astalegale.net** - Astalegale Network

Se nessuno di questi portali è accessibile (a causa di protezioni anti-scraping, manutenzione, o cambiamenti nella struttura HTML), l'applicazione passa automaticamente a **dati di esempio dimostrativi** che rispettano i filtri impostati.

### Come Usare l'App

1. **Imposta i Filtri:**
   - **Prezzo massimo**: Indica il budget massimo (es. 150000)
   - **Metri quadri minimi**: Superficie minima desiderata (es. 80)
   - **Zona geografica**: Città, provincia o regione (es. "Reggio Emilia")

2. **Clicca su "Analizza Immobili"**
   - Il sistema proverà a connettersi ai portali reali
   - Se trova dati, li mostrerà con match score
   - Se non trova nulla, userà dati di esempio

3. **Visualizza i Risultati:**
   - Gli immobili sono ordinati per corrispondenza
   - Ogni card mostra tutti i dettagli disponibili
   - Clicca su "Vedi offerta su IVG" per aprire la pagina ufficiale

## 🛠️ Struttura del Progetto

```
ivg-analyzer/
│
├── app.py                 # Server Flask (API)
├── ivg_scraper.py         # Logica di web scraping multi-source
├── index.html             # Frontend (interfaccia utente)
├── requirements.txt       # Dipendenze Python
├── start.bat             # Script avvio Windows
├── start.sh              # Script avvio Mac/Linux
├── README.md             # Questa guida
└── QUICKSTART.md         # Guida rapida
```

## ⚠️ Limitazioni del Web Scraping

### Perché potrebbero apparire dati di esempio?

I siti di aste giudiziarie moderni usano tecnologie che rendono difficile il scraping:

1. **JavaScript Rendering**: I contenuti sono generati dinamicamente
2. **Protezioni Anti-Bot**: Sistemi come Cloudflare, Captcha
3. **Struttura HTML Dinamica**: Cambia frequentemente
4. **Rate Limiting**: Limitazione richieste automatiche

### Soluzione Professionale

Per un sistema di produzione che funzioni sempre, sarebbe necessario:

- **Selenium/Playwright**: Browser automatizzato per JavaScript
- **API Ufficiali**: Se disponibili dai portali
- **Proxy Rotating**: Per evitare blocchi IP
- **Database**: Per cache e storico dati
- **Aggiornamenti Periodici**: Manutenzione continua

## 🔧 Configurazione Avanzata

### Modificare la Porta del Server

Apri `app.py` e modifica l'ultima riga:

```python
app.run(debug=True, host='0.0.0.0', port=8080)  # Cambia 5000 in 8080
```

Poi aggiorna anche `index.html` alla riga con `API_BASE_URL`:

```javascript
const API_BASE_URL = 'http://localhost:8080/api';  # Cambia 5000 in 8080
```

### Abilitare il Web Scraping Reale

Per migliorare il tasso di successo dello scraping:

1. Installa Selenium:
```bash
pip install selenium webdriver-manager
```

2. Il codice include già logiche per provare multiple fonti

3. Monitora i log nel terminale per vedere quali fonti funzionano

## 🌐 API Endpoints

### GET /api/health
Verifica lo stato del server.

**Risposta:**
```json
{
  "status": "ok",
  "message": "IVG API Server is running"
}
```

### POST /api/search
Cerca immobili con filtri.

**Body (JSON):**
```json
{
  "max_price": 150000,
  "min_size": 80,
  "location": "Reggio Emilia"
}
```

**Risposta:**
```json
{
  "success": true,
  "count": 5,
  "properties": [
    {
      "title": "Appartamento centro storico",
      "location": "Reggio Emilia, RE",
      "price": 95000,
      "size": 85,
      "rooms": 3,
      "floor": "2°",
      "condition": "Abitabile",
      "type": "Appartamento",
      "url": "https://www.astagiudiziaria.com/...",
      "matchScore": 85
    }
  ]
}
```

## 📊 Algoritmo di Match Score

Il sistema calcola un punteggio di corrispondenza (0-100%) basato su:

- **40% Prezzo**: Quanto l'immobile è sotto il budget massimo
- **30% Superficie**: Quanto l'immobile supera la superficie minima
- **30% Località**: Precisione della corrispondenza geografica

## 🔒 Note Legali e Privacy

- Questo software è destinato **esclusivamente a uso personale e didattico**
- Il web scraping deve rispettare i termini di servizio dei siti target
- Non utilizzare per scopi commerciali senza autorizzazione
- Limita la frequenza delle richieste per non sovraccaricare i siti
- I dati di esempio sono puramente dimostrativi

## 🎯 Sviluppi Futuri

Per un sistema di produzione completo, considera:

- [ ] **Selenium/Playwright** per scraping JavaScript-heavy sites
- [ ] **Database** (PostgreSQL/MySQL) per storico e cache
- [ ] **Scheduler** (Celery) per aggiornamenti automatici periodici
- [ ] **Notifiche Email** per nuovi immobili
- [ ] **Dashboard Analytics** con grafici prezzi
- [ ] **Sistema di Login** per salvataggio preferenze
- [ ] **Export Excel/PDF** dei risultati
- [ ] **Integrazione Telegram Bot** per notifiche real-time

## 💡 Supporto e Troubleshooting

### Il server non si avvia
- Verifica che Python sia installato: `python --version`
- Installa le dipendenze: `pip install -r requirements.txt`

### Vedo solo dati di esempio
- **È normale!** I siti usano protezioni anti-scraping
- L'app funziona come dimostrazione del concetto
- Per dati reali serve implementazione più avanzata (Selenium + proxy)

### Errore "Porta già in uso"
- Chiudi altre applicazioni che usano la porta 5000
- Oppure modifica la porta in `app.py` e `index.html`

### Come posso vedere dati reali?
- Visita direttamente i siti ufficiali:
  - https://www.astagiudiziaria.com/
  - https://www.astegiudiziarie.it/
  - https://www.astalegale.net/

## 📱 Contatti e Contributi

Questo è un progetto dimostrativo. Per implementazioni di produzione:

1. Considera l'uso di API ufficiali se disponibili
2. Implementa Selenium per bypass protezioni
3. Usa servizi di proxy professionali
4. Mantieni aggiornati i selettori HTML

---

**Versione:** 2.0.0  
**Data:** Gennaio 2026  
**Licenza:** Uso personale e educativo

**Disclaimer:** I dati di esempio vengono usati quando il scraping real-time non è disponibile. Per dati ufficiali, consulta sempre i portali governativi delle aste giudiziarie.

Buona ricerca! 🏠🔨
