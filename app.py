"""
IVG Real Estate API Server
Server Flask per l'applicazione di analisi immobili IVG
"""

from flask import Flask, jsonify, request, send_from_directory
from ivg_scraper import IVGScraper, calculate_match_score
import os

app = Flask(__name__)

# Configurazione CORS manuale (invece di flask-cors)
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    return response


@app.route('/')
def index():
    """Serve il frontend"""
    return send_from_directory('.', 'index.html')


@app.route('/api/search', methods=['GET', 'POST'])
def search_properties():
    """
    Endpoint per cercare immobili
    
    Parametri:
        - max_price: Prezzo massimo (float)
        - min_size: Superficie minima in mq (float)
        - location: Località (string)
    
    Returns:
        JSON con lista di immobili trovati e ordinati per match score
    """
    try:
        # Ottieni parametri dalla richiesta
        if request.method == 'POST':
            data = request.get_json()
            max_price = data.get('max_price')
            min_size = data.get('min_size')
            location = data.get('location')
        else:
            max_price = request.args.get('max_price', type=float)
            min_size = request.args.get('min_size', type=float)
            location = request.args.get('location', type=str)
        
        # Inizializza lo scraper
        scraper = IVGScraper()
        
        # Cerca immobili
        properties = scraper.search_properties(
            max_price=max_price,
            min_size=min_size,
            location=location
        )
        
        # Calcola il match score per ogni immobile
        for prop in properties:
            prop['matchScore'] = calculate_match_score(
                prop, max_price, min_size, location
            )
        
        # Ordina per match score decrescente
        properties.sort(key=lambda x: x['matchScore'], reverse=True)
        
        return jsonify({
            'success': True,
            'count': len(properties),
            'properties': properties
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'properties': []
        }), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Endpoint per verificare che il server sia attivo"""
    return jsonify({
        'status': 'ok',
        'message': 'IVG API Server is running'
    })


if __name__ == '__main__':
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║        🏛️  IVG Real Estate Analyzer API Server          ║
    ║                                                           ║
    ║  Server attivo su: http://localhost:5000                 ║
    ║                                                           ║
    ║  Endpoints disponibili:                                   ║
    ║  - GET  /                     → Frontend HTML            ║
    ║  - GET  /api/health           → Health check             ║
    ║  - GET  /api/search           → Cerca immobili           ║
    ║  - POST /api/search           → Cerca immobili (JSON)    ║
    ║                                                           ║
    ║  Premi CTRL+C per fermare il server                      ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
