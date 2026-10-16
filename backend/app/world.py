import math
import random
import uuid
import httpx
from .config import settings


def distance(a, b):
    lat1, lat2 = math.radians(a['lat']), math.radians(b['lat'])
    dl = math.radians(b['lng'] - a['lng'])
    h = math.sin((lat2-lat1)/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dl/2)**2
    return 6371000 * 2 * math.asin(min(1, math.sqrt(h)))


def offset(p, meters, bearing):
    return dict(lat=p['lat'] + meters * math.cos(bearing) / 111195,
                lng=p['lng'] + meters * math.sin(bearing) / (111195 * max(.01, math.cos(math.radians(p['lat'])))))


def generate_world(p):
    """Public footway geometry is a hint, never a guarantee of safe access."""
    candidates = []
    if settings().world_source == 'osm':
        query = f'''[out:json][timeout:6];way(around:1000,{p['lat']},{p['lng']})[highway~"^(footway|pedestrian|path|living_street)$"][access!~"private|no"][foot!~"private|no"][area!="yes"];out geom;'''
        try:
            response = httpx.post(settings().overpass_url, data={'data': query}, timeout=9)
            response.raise_for_status()
            for way in response.json().get('elements', []):
                for node in way.get('geometry', []):
                    q = dict(lat=node['lat'], lng=node['lon'])
                    if 100 <= distance(p, q) <= 1000 and all(distance(q, c) > 65 for c in candidates):
                        candidates.append(q)
        except (httpx.HTTPError, ValueError, KeyError):
            pass
    random.shuffle(candidates)
    cities = [c for c in candidates if 200 <= distance(p, c) <= 500]
    city = cities[0] if cities else None
    selected = [c for c in candidates if city and distance(c, city) > 65][:6]
    # A mixed fallback would hide which markers were verified. Flag the entire world instead.
    sourced = city is not None and len(selected) == 6
    if not sourced:
        bearing = random.uniform(0, math.tau)
        city = offset(p, random.uniform(220, 480), bearing)
        selected = [offset(p, random.uniform(120 + i * 130, 220 + i * 130),
                           bearing + i * math.tau / 6 + 1) for i in range(6)]
    names = ['Przepompownia', 'Stary wiadukt', 'Martwy sygnał', 'Zarośnięty magazyn', 'Cichy zaułek', 'Ostatni posterunek']
    points = [dict(id=str(uuid.uuid4()), type='city', name='Osada Iskra', **city)]
    points += [dict(id=str(uuid.uuid4()), type='spot', name=names[i], **q) for i, q in enumerate(selected)]
    for point in points:
        point.update(source='osm_paths' if sourced else 'demonstration', cooldown_until=0, encounter=None)
    return points
