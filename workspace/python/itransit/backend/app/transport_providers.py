import os
import logging
import httpx
from typing import List, Dict, Any, Optional

TRANSPORTAPI_APP_ID = os.getenv('TRANSPORTAPI_APP_ID')
TRANSPORTAPI_APP_KEY = os.getenv('TRANSPORTAPI_APP_KEY')
TFL_APP_KEY = os.getenv('TFL_APP_KEY')
TRANSLINK_KEY = os.getenv('TRANSLINK_KEY')
TRAVELINE_KEY = os.getenv('TRAVELINE_KEY')
TRAVELINE_URL = os.getenv('TRAVELINE_URL')
TRANSPORTSCOTLAND_KEY = os.getenv('TRANSPORTSCOTLAND_KEY')
TRANSPORTSCOTLAND_URL = os.getenv('TRANSPORTSCOTLAND_URL')
TFW_KEY = os.getenv('TFW_KEY')
TFW_URL = os.getenv('TFW_URL')

# logger: emits request parameter info to the server log so we can confirm keys are used
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


async def transportapi_nearby(lat: float, lon: float, radius: int, country: str) -> List[Dict[str, Any]]:
    """Use TransportAPI to find nearby stops. Requires TRANSPORTAPI_APP_ID and TRANSPORTAPI_APP_KEY."""
    if not (TRANSPORTAPI_APP_ID and TRANSPORTAPI_APP_KEY):
        return []
    url = "https://transportapi.com/v3/uk/places.json"
    params = {
        "app_id": TRANSPORTAPI_APP_ID,
        "app_key": TRANSPORTAPI_APP_KEY,
        "lat": lat,
        "lon": lon,
        "type": "bus_stop",
        "page": 1,
    }
    async with httpx.AsyncClient(timeout=10) as c:
        r = await c.get(url, params=params)
        if r.status_code != 200:
            return []
        data = r.json()
    places = []
    for p in data.get('member', []) or data.get('places', []):
        places.append({
            'stop_id': p.get('atcocode') or p.get('id') or p.get('name'),
            'name': p.get('name'),
            'lat': p.get('latitude'),
            'lon': p.get('longitude'),
            'modes': p.get('modes', ['bus']),
            'distance_m': int(p.get('distance', 0)) if p.get('distance') is not None else 0,
        })
    return places


async def transportapi_departures(stop_id: str) -> List[Dict[str, Any]]:
    # TransportAPI offers live departures via different endpoints; try a common pattern
    if not (TRANSPORTAPI_APP_ID and TRANSPORTAPI_APP_KEY):
        return []
    url = f"https://transportapi.com/v3/uk/stops/{stop_id}/live.json"
    params = {"app_id": TRANSPORTAPI_APP_ID, "app_key": TRANSPORTAPI_APP_KEY, "darwin": "true", "train_status": "passenger"}
    async with httpx.AsyncClient(timeout=10) as c:
        r = await c.get(url, params=params)
        if r.status_code != 200:
            return []
        data = r.json()
    outs = []
    # bus departures often under 'departures'->'all'
    for mode_deps in data.get('departures', {}).values():
        for d in mode_deps:
            outs.append({'line': d.get('line') or d.get('service'), 'destination': d.get('direction') or d.get('destination_name'), 'expected_minutes': d.get('best_departure_estimate_minutes', 0) or d.get('expected_minutes', 0)})
    return outs


async def tfl_nearby(lat: float, lon: float, radius: int, country: str) -> List[Dict[str, Any]]:
    """Query TfL StopPoint API. No key required for many endpoints but a key may increase rate limits."""
    url = "https://api.tfl.gov.uk/StopPoint"
    params = {"lat": lat, "lon": lon, "stopTypes": "NaptanPublicBusCoachTram", "radius": radius}
    if TFL_APP_KEY:
        params['app_key'] = TFL_APP_KEY
    logger.info('TfL StopPoint request params: %s', {k: ('<REDACTED>' if k.lower().find('key')!=-1 else v) for k, v in params.items()})
    async with httpx.AsyncClient(timeout=10) as c:
        r = await c.get(url, params=params)
        if r.status_code != 200:
            return []
        data = r.json()
    res = []
    for item in data.get('stopPoints', []) if isinstance(data, dict) else data:
        res.append({'stop_id': item.get('naptanId') or item.get('icsCode') or item.get('id'), 'name': item.get('commonName') or item.get('name'), 'lat': item.get('lat') or item.get('latitude'), 'lon': item.get('lon') or item.get('longitude'), 'modes': item.get('modes', []), 'distance_m': item.get('distance', 0)})
    return res


async def tfl_departures(stop_id: str) -> List[Dict[str, Any]]:
    url = f"https://api.tfl.gov.uk/StopPoint/{stop_id}/Arrivals"
    params = {}
    if TFL_APP_KEY:
        params['app_key'] = TFL_APP_KEY
    logger.info('TfL Arrivals request URL: %s params: %s', url, {k: ('<REDACTED>' if k.lower().find('key')!=-1 else v) for k, v in params.items()})
    async with httpx.AsyncClient(timeout=10) as c:
        r = await c.get(url, params=params)
        if r.status_code != 200:
            return []
        data = r.json()
    outs = []
    for d in data:
        mins = None
        if d.get('timeToStation') is not None:
            mins = int(d['timeToStation'] / 60)
        outs.append({'line': d.get('lineName'), 'destination': d.get('destinationName'), 'expected_minutes': mins if mins is not None else 0})
    outs.sort(key=lambda x: x['expected_minutes'])
    return outs


async def translink_nearby(lat: float, lon: float, radius: int, country: str) -> List[Dict[str, Any]]:
    # Translink API requires a key from developer.translink.co.uk — if not present, return []
    if not TRANSLINK_KEY:
        return []
    # Example: use generic stops search endpoint (placeholder)
    url = "https://data.nisra.gov.uk/translink/stoppoints"  # placeholder — user should provide exact endpoint/key
    async with httpx.AsyncClient(timeout=10) as c:
        try:
            r = await c.get(url, params={'lat': lat, 'lon': lon, 'radius': radius, 'apikey': TRANSLINK_KEY})
            if r.status_code != 200:
                return []
            data = r.json()
        except Exception:
            return []
    res = []
    for p in data.get('results', []):
        res.append({'stop_id': p.get('stop_id'), 'name': p.get('stop_name'), 'lat': p.get('latitude'), 'lon': p.get('longitude'), 'modes': p.get('modes', []), 'distance_m': p.get('distance', 0)})
    return res


async def translink_departures(stop_id: str) -> List[Dict[str, Any]]:
    if not TRANSLINK_KEY:
        return []
    url = f"https://developer.translink.co.uk/odata/StopMonitoring?$filter=StopPointRef eq '{stop_id}'"
    headers = { 'Ocp-Apim-Subscription-Key': TRANSLINK_KEY }
    async with httpx.AsyncClient(timeout=10) as c:
        r = await c.get(url, headers=headers)
        if r.status_code != 200:
            return []
        data = r.json()
    outs = []
    for e in data.get('value', []):
        outs.append({'line': e.get('MonitoredVehicleJourney', {}).get('PublishedLineName'), 'destination': e.get('MonitoredVehicleJourney', {}).get('DestinationName'), 'expected_minutes': 0})
    return outs


async def traveline_nearby(lat: float, lon: float, radius: int, country: str) -> List[Dict[str, Any]]:
    # Traveline APIs differ by region; require TRAVELINE_URL and possibly TRAVELINE_KEY
    if not TRAVELINE_URL:
        return []
    params = {"lat": lat, "lon": lon, "radius": radius}
    headers = {}
    if TRAVELINE_KEY:
        headers['Authorization'] = f"Bearer {TRAVELINE_KEY}"
    async with httpx.AsyncClient(timeout=10) as c:
        try:
            r = await c.get(TRAVELINE_URL.rstrip('/') + '/places.json', params=params, headers=headers)
            if r.status_code != 200:
                return []
            data = r.json()
        except Exception:
            return []
    res = []
    for p in data.get('places', []) if isinstance(data, dict) else []:
        res.append({'stop_id': p.get('id') or p.get('atcocode'), 'name': p.get('name'), 'lat': p.get('latitude') or p.get('lat'), 'lon': p.get('longitude') or p.get('lon'), 'modes': p.get('modes', []), 'distance_m': p.get('distance', 0)})
    return res


async def traveline_departures(stop_id: str) -> List[Dict[str, Any]]:
    if not TRAVELINE_URL:
        return []
    headers = {}
    if TRAVELINE_KEY:
        headers['Authorization'] = f"Bearer {TRAVELINE_KEY}"
    async with httpx.AsyncClient(timeout=10) as c:
        try:
            r = await c.get(TRAVELINE_URL.rstrip('/') + f'/stops/{stop_id}/departures.json', headers=headers)
            if r.status_code != 200:
                return []
            data = r.json()
        except Exception:
            return []
    outs = []
    for d in data.get('departures', []) if isinstance(data, dict) else []:
        outs.append({'line': d.get('line'), 'destination': d.get('destination'), 'expected_minutes': d.get('expected_minutes', 0)})
    return outs


async def transportscotland_nearby(lat: float, lon: float, radius: int, country: str) -> List[Dict[str, Any]]:
    # Transport Scotland publishes datasets; if a custom API URL is provided use it
    if not TRANSPORTSCOTLAND_URL:
        return []
    params = {"lat": lat, "lon": lon, "radius": radius}
    headers = {}
    if TRANSPORTSCOTLAND_KEY:
        headers['Authorization'] = f"Bearer {TRANSPORTSCOTLAND_KEY}"
    async with httpx.AsyncClient(timeout=10) as c:
        try:
            r = await c.get(TRANSPORTSCOTLAND_URL.rstrip('/') + '/places.json', params=params, headers=headers)
            if r.status_code != 200:
                return []
            data = r.json()
        except Exception:
            return []
    res = []
    for p in data.get('places', []) if isinstance(data, dict) else []:
        res.append({'stop_id': p.get('id'), 'name': p.get('name'), 'lat': p.get('latitude') or p.get('lat'), 'lon': p.get('longitude') or p.get('lon'), 'modes': p.get('modes', []), 'distance_m': p.get('distance', 0)})
    return res


async def transportscotland_departures(stop_id: str) -> List[Dict[str, Any]]:
    if not TRANSPORTSCOTLAND_URL:
        return []
    headers = {}
    if TRANSPORTSCOTLAND_KEY:
        headers['Authorization'] = f"Bearer {TRANSPORTSCOTLAND_KEY}"
    async with httpx.AsyncClient(timeout=10) as c:
        try:
            r = await c.get(TRANSPORTSCOTLAND_URL.rstrip('/') + f'/stops/{stop_id}/departures.json', headers=headers)
            if r.status_code != 200:
                return []
            data = r.json()
        except Exception:
            return []
    outs = []
    for d in data.get('departures', []) if isinstance(data, dict) else []:
        outs.append({'line': d.get('line'), 'destination': d.get('destination'), 'expected_minutes': d.get('expected_minutes', 0)})
    return outs


async def tfw_nearby(lat: float, lon: float, radius: int, country: str) -> List[Dict[str, Any]]:
    # Transport for Wales: allow custom endpoint via TFW_URL
    if not TFW_URL:
        return []
    params = {"lat": lat, "lon": lon, "radius": radius}
    headers = {}
    if TFW_KEY:
        headers['Authorization'] = f"Bearer {TFW_KEY}"
    async with httpx.AsyncClient(timeout=10) as c:
        try:
            r = await c.get(TFW_URL.rstrip('/') + '/places.json', params=params, headers=headers)
            if r.status_code != 200:
                return []
            data = r.json()
        except Exception:
            return []
    res = []
    for p in data.get('places', []) if isinstance(data, dict) else []:
        res.append({'stop_id': p.get('id'), 'name': p.get('name'), 'lat': p.get('latitude') or p.get('lat'), 'lon': p.get('longitude') or p.get('lon'), 'modes': p.get('modes', []), 'distance_m': p.get('distance', 0)})
    return res


async def tfw_departures(stop_id: str) -> List[Dict[str, Any]]:
    if not TFW_URL:
        return []
    headers = {}
    if TFW_KEY:
        headers['Authorization'] = f"Bearer {TFW_KEY}"
    async with httpx.AsyncClient(timeout=10) as c:
        try:
            r = await c.get(TFW_URL.rstrip('/') + f'/stops/{stop_id}/departures.json', headers=headers)
            if r.status_code != 200:
                return []
            data = r.json()
        except Exception:
            return []
    outs = []
    for d in data.get('departures', []) if isinstance(data, dict) else []:
        outs.append({'line': d.get('line'), 'destination': d.get('destination'), 'expected_minutes': d.get('expected_minutes', 0)})
    return outs


async def get_nearby(lat: float, lon: float, radius: int, country: str):
    """Top-level chooser: try provider(s) appropriate for country, falling back to TfL/TransportAPI then mock."""
    country = (country or '').lower()
    # London -> TfL
    if 'london' in country or country.strip().lower() == 'england':
        # try TfL first, then TransportAPI
        res = await tfl_nearby(lat, lon, radius, country)
        if res:
            return res
        res = await transportapi_nearby(lat, lon, radius, country)
        return res
    if 'scotland' in country:
        # try specialised providers: Transport Scotland, Traveline Scotland, then TransportAPI
        res = await transportscotland_nearby(lat, lon, radius, country)
        if res:
            return res
        res = await traveline_nearby(lat, lon, radius, country)
        if res:
            return res
        res = await transportapi_nearby(lat, lon, radius, country)
        return res
    if 'wales' in country:
        # try Transport for Wales, then TransportAPI
        res = await tfw_nearby(lat, lon, radius, country)
        if res:
            return res
        res = await transportapi_nearby(lat, lon, radius, country)
        return res
    if 'northern' in country or 'ireland' in country:
        res = await translink_nearby(lat, lon, radius, country)
        if res:
            return res
        return await transportapi_nearby(lat, lon, radius, country)
    # default: try TransportAPI then TfL
    res = await transportapi_nearby(lat, lon, radius, country)
    if res:
        return res
    return await tfl_nearby(lat, lon, radius, country)


async def get_departures(stop_id: str, country: str):
    country = (country or '').lower()
    if 'london' in country or country.strip().lower() == 'england':
        out = await tfl_departures(stop_id)
        if out:
            return out
        out = await transportapi_departures(stop_id)
        return out
    if 'northern' in country or 'ireland' in country:
        out = await translink_departures(stop_id)
        if out:
            return out
        return await transportapi_departures(stop_id)
    if 'scotland' in country:
        out = await transportscotland_departures(stop_id)
        if out:
            return out
        out = await traveline_departures(stop_id)
        if out:
            return out
        return await transportapi_departures(stop_id)
    if 'wales' in country:
        out = await tfw_departures(stop_id)
        if out:
            return out
        return await transportapi_departures(stop_id)
    # default
    out = await transportapi_departures(stop_id)
    if out:
        return out
    return await tfl_departures(stop_id)
