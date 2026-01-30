"""
IVG Real Estate API Server
Server Flask per l'applicazione di analisi immobili IVG
"""

from flask import Flask, jsonify, request, send_from_directory
from ivg_scraper import IVGScraper, calculate_match_score
import os

app = Flask(__name__)

# CORS (opzionale, ma ok)
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    return response


@app.route('/')
def index():
    return send_from_directory('.', 'index.html')


@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'ok',
        'message': 'IVG API Server is running'
    })


@app.route('/api/search', methods=['GET', 'POST'])
def search_properties():
    try:
        if request.method == 'POST':
            data = request.get_json() or {}
            max_price = data.get('max_price')
            min_size = data.get('min_size')
            location = data.get('location')
            locazione = data.get('locazione')
            stato = data.get('stato')
        else:
            max_price = request.args.get('max_price', type=float)
            min_size = request.args.get('min_size', type=float)
            location = request.args.get('location', type=str)
            locazione = data.get('locazione')
            stato = data.get('stato')

        scraper = IVGScraper()

        properties = scraper.search_properties(
            max_price=max_price,
            min_size=min_size,
            location=location,
            locazione = locazione,
            stato = stato,
        )

        for prop in properties:
            prop['matchScore'] = calculate_match_score(
                prop, max_price, min_size, location, locazione, stato
            )

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


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))

    print(f"""
╔═══════════════════════════════════════════════════════════╗
║ 🏛️  IVG Real Estate Analyzer API Server                   ║
║ Server avviato su porta {port}                            ║
║ Endpoints:                                                ║
║  - GET  /api/health                                      ║
║  - GET  /api/search                                      ║
║  - POST /api/search                                      ║
╚═══════════════════════════════════════════════════════════╝
""")

    app.run(host="0.0.0.0", port=port)
