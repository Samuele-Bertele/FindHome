"""
IVG Real Estate Scraper - Versione Migliorata
Scraper robusto con multiple fonti e metodi di fallback
"""

import requests
from bs4 import BeautifulSoup
import re
import json
from typing import List, Dict, Optional
from urllib.parse import urljoin
import time


class IVGScraper:
    """Scraper migliorato per aste giudiziarie (usa tutti gli input del frontend)"""
    SOURCES = [
        {'name': 'astagiudiziaria', 'base_url': 'https://www.astagiudiziaria.com', 'search_url': 'https://www.astagiudiziaria.com/ricerca/immobili'},
        {'name': 'astegiudiziarie', 'base_url': 'https://www.astegiudiziarie.it', 'search_url': 'https://www.astegiudiziarie.it/immobili'},
        {'name': 'astalegale', 'base_url': 'https://www.astalegale.net', 'search_url': 'https://www.astalegale.net/risultati-ricerca'}
    ]

    def __init__(self, timeout: int = 10):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'it-IT,it;q=0.9,en;q=0.8',
        })
        self.timeout = timeout

    def search_properties(self,
                          max_price: Optional[float] = None,
                          min_size: Optional[float] = None,
                          location: Optional[str] = None,
                          home_apartment: Optional[str] = None,
                          locazione: Optional[str] = None,
                          stato: Optional[str] = None) -> List[Dict]:
        """
        Cerca immobili usando tutte le variabili dal frontend.
        Restituisce lista (vuota se non trova nulla).
        """
        all_properties: List[Dict] = []

        for source in self.SOURCES:
            try:
                print(f"[scraper] Tentativo con {source['name']}...")
                properties = self._scrape_source(
                    source,
                    max_price=max_price,
                    min_size=min_size,
                    location=location,
                    home_apartment=home_apartment,
                    locazione=locazione,
                    stato=stato
                )
                if properties:
                    print(f"[scraper] ✓ Trovati {len(properties)} immobili da {source['name']}")
                    all_properties.extend(properties)
                    if len(all_properties) >= 50:  # limite aggregazione
                        break
                else:
                    print(f"[scraper] ✗ Nessun risultato da {source['name']}")
            except Exception as e:
                print(f"[scraper] Errore con {source['name']}: {e}")
                continue
            time.sleep(0.8)

        # NON generiamo dati finti: se non trovi nulla, ritorniamo lista vuota
        return all_properties

    def _scrape_source(self, source: Dict, max_price: Optional[float],
                       min_size: Optional[float], location: Optional[str],
                       home_apartment: Optional[str], locazione: Optional[str],
                       stato: Optional[str]) -> List[Dict]:
        properties: List[Dict] = []
        try:
            params = {}
            # proviamo a mappare i campi ai parametri di ricerca comuni dei siti
            if location:
                params.update({'comune': location, 'citta': location, 'provincia': location})
            if max_price:
                params['prezzoMax'] = int(max_price)
            if min_size:
                params['superficieMin'] = int(min_size)
            # tipologia / stato possono anche essere passati come parametri (se il sito li supporta)
            if home_apartment:
                params['tipologia'] = home_apartment
            if stato:
                params['stato'] = stato
            if locazione:
                params['locazione'] = locazione

            response = self.session.get(source['search_url'], params=params or None, timeout=self.timeout)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            # Prima prova: JSON embedded
            json_data = self._extract_json_data(soup)
            if json_data:
                properties = self._parse_json_data(json_data, source['base_url'],
                                                   max_price, min_size, location,
                                                   home_apartment, locazione, stato)

            # Seconda: parsing HTML
            if not properties:
                properties = self._parse_html_listings(soup, source['base_url'],
                                                       max_price, min_size, location,
                                                       home_apartment, locazione, stato)
        except Exception as e:
            print(f"[scraper] Errore scraping {source['name']}: {e}")
        return properties

    def _extract_json_data(self, soup) -> Optional[Dict]:
        # script type application/ld+json
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                data = json.loads(script.string)
                if isinstance(data, (dict, list)):
                    return data
            except Exception:
                continue
        # script con window.__DATA__ o simili
        for script in soup.find_all('script'):
            txt = script.string
            if not txt:
                continue
            if 'window.__DATA__' in txt or 'window.initialData' in txt or 'var listings' in txt:
                match = re.search(r'(\{.*\}|\[.*\])', txt, re.DOTALL)
                if match:
                    try:
                        return json.loads(match.group(1))
                    except Exception:
                        continue
        return None

    def _parse_json_data(self, data: Dict, base_url: str,
                         max_price: Optional[float], min_size: Optional[float], location: Optional[str],
                         home_apartment: Optional[str], locazione: Optional[str], stato: Optional[str]) -> List[Dict]:
        """
        Tentativo generico di estrazione da JSON embedded.
        Ogni sito ha il suo formato: qui tentiamo di estrarre proprietà standard se presenti.
        """
        properties: List[Dict] = []

        try:
            items = []
            if isinstance(data, dict) and 'itemListElement' in data:
                items = data.get('itemListElement') or []
            elif isinstance(data, list):
                items = data
            elif isinstance(data, dict):
                # prova a trovare chiavi comuni
                for key in ('listings', 'offers', 'results', 'items', 'properties'):
                    if key in data and isinstance(data[key], list):
                        items = data[key]; break

            for item in items:
                if not isinstance(item, dict):
                    # alcuni itemListElement contengono wrapper con 'item'
                    if isinstance(item, dict) and 'item' in item and isinstance(item['item'], dict):
                        item = item['item']
                    else:
                        continue

                title = item.get('name') or item.get('title') or item.get('headline') or ''
                price = 0.0
                size = 0.0
                url = ''
                location_field = ''
                rooms = item.get('rooms') or item.get('bedrooms') or 0
                condition = item.get('condition') or item.get('state') or ''
                # offer/price
                if 'offers' in item:
                    offers = item.get('offers')
                    if isinstance(offers, dict):
                        price = float(offers.get('price', 0) or 0)
                    elif isinstance(offers, list) and offers:
                        try:
                            price = float(offers[0].get('price', 0) or 0)
                        except:
                            price = 0.0
                elif 'price' in item:
                    try:
                        price = float(item.get('price') or 0)
                    except:
                        price = 0.0

                # area
                if 'floorSize' in item:
                    fs = item.get('floorSize')
                    if isinstance(fs, dict) and 'value' in fs:
                        try:
                            size = float(fs.get('value') or 0)
                        except:
                            size = 0.0
                    else:
                        try:
                            size = float(fs)
                        except:
                            size = 0.0
                elif 'area' in item:
                    try:
                        size = float(item.get('area') or 0)
                    except:
                        size = 0.0

                if 'url' in item:
                    url = urljoin(base_url, item.get('url'))
                if 'address' in item:
                    addr = item.get('address')
                    if isinstance(addr, dict):
                        location_field = addr.get('addressLocality') or addr.get('addressRegion') or ''
                    else:
                        location_field = str(addr)

                # calcola price_per_m2
                price_per_m2 = round(price / size, 2) if price and size else None

                prop = {
                    'title': title[:200] if title else 'Immobile in asta',
                    'location': location_field or '',
                    'price': price,
                    'price_per_m2': price_per_m2,
                    'size': size,
                    'rooms': int(rooms or 0),
                    'floor': item.get('floor') or 'Non specificato',
                    'condition': condition or 'Da verificare',
                    'type': item.get('propertyType') or item.get('type') or home_apartment or 'Immobile',
                    'auction_type': item.get('occupancy') or ('Occupato' if 'occupato' in (item.get('description') or '').lower() else 'Libero'),
                    'auction_date': item.get('auctionDate') or item.get('date') or 'Da definire',
                    'url': url or base_url
                }

                # Applica filtri minimi lato parsing per rispettare i criteri richiesti
                if max_price and prop['price'] and prop['price'] > max_price:
                    continue
                if min_size and prop['size'] and prop['size'] < min_size:
                    continue
                # filtro location basico
                if location and prop['location'] and location.lower() not in prop['location'].lower():
                    continue

                properties.append(prop)
        except Exception as e:
            print("[scraper] Errore parse JSON:", e)

        return properties

    def _parse_html_listings(self, soup, base_url: str,
                             max_price: Optional[float], min_size: Optional[float], location: Optional[str],
                             home_apartment: Optional[str], locazione: Optional[str], stato: Optional[str]) -> List[Dict]:
        properties: List[Dict] = []

        card_selectors = [
            {'class_': re.compile(r'asta|lotto|property|immobile|card|risultato|inserzione', re.IGNORECASE)},
            {'class_': 'result-item'},
            {'class_': 'listing'},
            {'attrs': {'data-id': True}},
            {'attrs': {'data-lotto': True}}
        ]

        cards = []
        for selector in card_selectors:
            try:
                found = soup.find_all('div', **selector)
            except Exception:
                found = []
            if found:
                cards = found
                break

        if not cards:
            cards = soup.find_all(['article', 'li'], class_=re.compile(r'asta|property|lotto', re.IGNORECASE))

        for card in cards[:50]:
            try:
                prop = self._parse_property_card(card, base_url)
                if not prop:
                    continue
                # filtri
                if max_price and prop.get('price') and prop['price'] > max_price:
                    continue
                if min_size and prop.get('size') and prop['size'] < min_size:
                    continue
                if location and prop.get('location') and location.lower() not in prop['location'].lower():
                    continue
                # filtro per tipo/stato/locazione (se forniti) - confronto permissivo
                # Non scartiamo rigidamente se mancano campi
                properties.append(prop)
            except Exception:
                continue

        return properties

    def _parse_property_card(self, card, base_url: str) -> Optional[Dict]:
        """Estrae dati da una singola card, con campi migliorati per frontend"""
        try:
            price_text = card.get_text(" ", strip=True)
            title_elem = card.find(['h2', 'h3', 'h4', 'a'])
            title = title_elem.get_text(strip=True) if title_elem else "Immobile in asta"

            # prezzo (ricerca flessibile)
            price = 0.0
            price_match = re.search(r'€\s*([0-9\.\s]+(?:,[0-9]{2})?)', price_text)
            if price_match:
                p = price_match.group(1).strip().replace(' ', '').replace('.', '').replace(',', '.')
                try:
                    price = float(p)
                except:
                    price = 0.0

            # superficie
            size = 0.0
            size_match = re.search(r'(\d+(?:[\.,]\d+)?)\s*(?:mq|m²|m2|metri)', price_text, re.IGNORECASE)
            if size_match:
                try:
                    size = float(size_match.group(1).replace(',', '.'))
                except:
                    size = 0.0

            price_per_m2 = round(price / size, 2) if price and size else None

            # localita' (tentativi multipli)
            location = ""
            loc_match = re.search(r'\(([A-Z]{2})\)', price_text)
            if loc_match:
                location = loc_match.group(0)
            else:
                comuni_pattern = re.compile(
                    r'\b(Roma|Milano|Napoli|Torino|Palermo|Genova|Bologna|Firenze|Bari|Catania|Venezia|Verona|Reggio\s+Emilia|Modena|Parma|Piacenza|Brescia)\b',
                    re.IGNORECASE)
                m = comuni_pattern.search(price_text)
                if m:
                    location = m.group(0)

            # url
            a = card.find('a', href=True)
            url = urljoin(base_url, a['href']) if a else base_url

            # rooms
            rooms = 0
            r = re.search(r'(\d+)\s*(?:local|vani|stanze)', price_text, re.IGNORECASE)
            if r:
                try:
                    rooms = int(r.group(1))
                except:
                    rooms = 0

            # floor
            f = re.search(r'(terra|primo|secondo|terzo|quarto|attico|\d+°?)', price_text, re.IGNORECASE)
            floor = f.group(0).capitalize() if f else 'Non specificato'

            # condition
            cond = re.search(r'(abitabile|da ristrutturare|nuovo|ottimo stato|buono stato)', price_text, re.IGNORECASE)
            condition = cond.group(0).capitalize() if cond else 'Da verificare'

            # type
            t = re.search(r'(appartamento|casa|attico|villa|loft|bilocale|trilocale)', price_text, re.IGNORECASE)
            type_ = t.group(0).capitalize() if t else 'Immobile'

            # auction_type
            auction_type = 'Occupato' if 'occupato' in price_text.lower() else 'Libero'

            # auction_date
            d = re.search(r'(\d{1,2}/\d{1,2}/\d{4})', price_text)
            auction_date = d.group(0) if d else 'Da definire'

            return {
                'title': title[:200],
                'location': location,
                'price': price,
                'price_per_m2': price_per_m2,
                'size': size,
                'rooms': rooms,
                'floor': floor,
                'condition': condition,
                'type': type_,
                'auction_type': auction_type,
                'auction_date': auction_date,
                'url': url
            }
        except Exception:
            # in caso di problemi sul singolo card, non blocchiamo l'intero scraping
            return None


def calculate_match_score(property_data: Dict,
                          max_price: Optional[float],
                          min_size: Optional[float],
                          location: Optional[str],
                          home_apartment: Optional[str] = None,
                          locazione: Optional[str] = None,
                          stato: Optional[str] = None) -> int:
    score = 0

    # prezzo: meglio se sotto il limite
    if max_price and max_price > 0 and property_data.get('price', 0) > 0:
        price_ratio = max(0.0, (max_price - property_data['price']) / max_price)
        score += int(min(40, price_ratio * 40))

    # dimensione: meglio se >= richiesta
    if min_size and min_size > 0 and property_data.get('size', 0) > 0:
        # rapporto rispetto alla richiesta (più è grande rispetto a richiesta, meglio)
        size_ratio = max(0.0, (property_data['size'] - min_size) / max(property_data['size'], 1))
        score += int(min(25, size_ratio * 25))

    # location
    if location and property_data.get('location'):
        prop_loc = property_data['location'].lower()
        loc_lower = location.lower()
        if loc_lower == prop_loc.split(',')[0].strip():
            score += 20
        elif loc_lower in prop_loc:
            score += 12
        elif any(w in prop_loc for w in loc_lower.split()):
            score += 6

    # locazione (se presente in testo)
    if locazione and property_data.get('type'):
        if locazione.lower() in (property_data.get('type', '') + ' ' + property_data.get('condition', '')).lower():
            score += 4

    # stato
    if stato and property_data.get('condition'):
        if stato.lower() in property_data['condition'].lower():
            score += 4

    return min(100, score)

if __name__ == "__main__":
    # Test
    scraper = IVGScraper()
    print("=== Test IVG Scraper ===\n")

    results = scraper.search_properties(
        max_price=150000,
        min_size=70,
        location="Reggio Emilia",
        locazione="Appartamento",
        stato="Abitabile"
    )

    print(f"\n=== Risultati: {len(results)} immobili ===\n")
    for i, prop in enumerate(results[:5], 1):
        title = prop.get('title', 'N/D')
        price = prop.get('price', 0)
        size = prop.get('size', 0)
        location_txt = prop.get('location', '')
        url = prop.get('url', '')
        print(f"{i}. {title}")
        print(f"   Prezzo: €{price:,.0f}")
        print(f"   Superficie: {size} m²")
        print(f"   Località: {location_txt}")
        print(f"   URL: {url}")
        ppm = prop.get('price_per_m2')
        if ppm:
            print(f"   Prezzo €/m²: €{ppm}")
        print(f"   Tipologia: {prop.get('type', 'N/D')}")
        print(f"   Stato: {prop.get('condition', 'N/D')}")
        print(f"   Piano: {prop.get('floor', 'N/D')}")
        print(f"   Stato asta: {prop.get('auction_type', 'N/D')}")
        print(f"   Data asta: {prop.get('auction_date', 'N/D')}\n")
