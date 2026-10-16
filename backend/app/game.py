import random
import time
import uuid
from datetime import datetime
from zoneinfo import ZoneInfo
from fastapi import HTTPException
from .catalog import ITEMS, ENEMIES, SETTLEMENTS, BASE_ATTACK, BASE_HP, max_hp, stats, xp_threshold
from .config import settings
from .world import distance

RNG = random.SystemRandom()


def fail(message, code=400):
    raise HTTPException(code, message)


def validate_fix(fix, now=None):
    now = now or time.time()
    if not -90 <= fix['lat'] <= 90 or not -180 <= fix['lng'] <= 180:
        fail('Nieprawidłowe współrzędne.')
    if not 0 < fix['accuracy'] <= settings().max_accuracy_m:
        fail(f"Lokalizacja jest zbyt niedokładna. Wymagana dokładność do {settings().max_accuracy_m} m.")
    if not -5 <= now - fix['timestamp'] <= settings().location_max_age_s:
        fail('Lokalizacja wygasła. Poczekaj na nowy pomiar GPS.')
    if fix.get('demo') and not settings().demo_enabled:
        fail('Tryb demonstracyjny jest wyłączony.', 403)


def point_access(s, point_id, fix):
    validate_fix(fix)
    point = next((p for p in s['points'] if p['id'] == point_id), None)
    if not point:
        fail('Nie znaleziono miejsca.', 404)
    if distance(point, fix) > settings().interaction_radius_m:
        fail('Jesteś poza zasięgiem tego miejsca.', 403)
    return point


def today():
    return datetime.now(ZoneInfo('Europe/Warsaw')).date().isoformat()


def refresh_state(s, now=None):
    """Upgrade older saves and settle whole minutes, including time spent offline."""
    now = time.time() if now is None else now
    s.setdefault('nickname', None)
    for point in s['points']:
        if point['type'] == 'city':
            point.setdefault('settlement', 'settlement')
            point['name'] = SETTLEMENTS[point['settlement']]['name']
    # Convert saves from the temporary choice system while preserving missing HP.
    if 'upgrades' in s or 'upgrade_points' in s:
        previous_max = BASE_HP + s.get('upgrades', {}).get('hp', max_hp(s) - BASE_HP)
        s['hp'] = min(max_hp(s), s['hp'] + max(0, max_hp(s) - previous_max))
        s.pop('upgrades', None)
        s.pop('upgrade_points', None)
    s.setdefault('regen_at', now)
    if s['battle'] or s['hp'] >= max_hp(s):
        s['regen_at'] = None
        return
    if s['regen_at'] is None:
        s['regen_at'] = now
    minutes = max(0, int((now - s['regen_at']) // 60))
    if minutes:
        s['hp'] = min(max_hp(s), s['hp'] + minutes)
        s['regen_at'] = now if s['hp'] == max_hp(s) else s['regen_at'] + minutes * 60


def public_state(s):
    # Only current location and aggregate distance are stored, never a full route.
    return {**{k: v for k, v in s.items() if k not in ('regen_at', 'cleared_areas')},
            'regen_next_at': s.get('regen_at') + 60 if s.get('regen_at') and not s['battle'] and s['hp'] < max_hp(s) else None,
            'max_hp': max_hp(s), 'xp_next': xp_threshold(s['level']),
            'stats': stats(s), 'today_distance': s['daily'].get(today(), 0)}


def inventory_add(s, item, amount):
    s['inventory'][item] = s['inventory'].get(item, 0) + amount
    if s['inventory'][item] <= 0:
        del s['inventory'][item]


def medkit(s):
    if s['hp'] >= max_hp(s):
        fail('Masz już pełne HP.')
    if s['inventory'].get('medkit', 0) < 1:
        fail('Nie masz apteczki.')
    inventory_add(s, 'medkit', -1)
    before = s['hp']
    s['hp'] = min(max_hp(s), s['hp'] + ITEMS['medkit']['heal'])
    s['regen_at'] = time.time()
    return s['hp'] - before


def encounter(point):
    if point['cooldown_until'] > time.time():
        fail('Miejsce odpoczywa po ostatniej walce. Poczekaj na koniec odnowienia.')
    if point['encounter'] is None:
        point['encounter'] = [dict(kind=k, **ENEMIES[k], max_hp=ENEMIES[k]['hp'])
                              for k in [RNG.choice(list(ENEMIES)) for _ in range(RNG.randint(1, 3))]]
    return point['encounter']


def start_battle(s, point):
    if s['battle']:
        fail('Masz już aktywną walkę.')
    if point['type'] != 'spot':
        fail('W tym miejscu nie ma przeciwników.')
    enemies = encounter(point)
    s['battle'] = dict(id=str(uuid.uuid4()), point_id=point['id'], enemies=enemies,
                       index=0, log=['Rozpoczynasz walkę.'], turn=0)
    s['last_battle'] = None
    s['regen_at'] = time.time()


def finish_battle(s, result):
    b = s['battle']
    p = next(p for p in s['points'] if p['id'] == b['point_id'])
    rewards = dict(gold=0, xp=0, loot={})
    if result == 'victory':
        rewards['gold'] = sum(e['gold'] for e in b['enemies'])
        rewards['xp'] = sum(e['xp'] for e in b['enemies'])
        loot = RNG.choice(['scrap', 'electronics', 'medkit', 'ammo', 'grenade'])
        rewards['loot'] = {loot: RNG.randint(4, 12) if loot == 'ammo' else RNG.randint(1, 2)}
        s['gold'] += rewards['gold']
        s['xp'] += rewards['xp']
        for item, qty in rewards['loot'].items():
            inventory_add(s, item, qty)
        levels = 0
        while s['xp'] >= xp_threshold(s['level']):
            s['xp'] -= xp_threshold(s['level'])
            s['level'] += 1
            levels += 1
        if levels:
            s['hp'] = max_hp(s)
        rewards['levels'] = levels
    if result == 'defeat':
        s['hp'] = max(1, round(max_hp(s) * .4))
    p['cooldown_until'] = time.time() + (settings().cooldown_seconds if result == 'victory' else settings().defeat_cooldown_seconds)
    p['encounter'] = None
    s['last_battle'] = dict(id=b['id'], result=result, rewards=rewards, log=b['log'][-12:])
    s['battle'] = None
    s['regen_at'] = time.time()


def battle_action(s, battle_id, turn, action):
    b = s['battle']
    if not b or b['id'] != battle_id:
        fail('Ta walka nie jest już aktywna.', 409)
    if turn != b['turn']:
        fail('Tura została już wykonana. Odśwież stan walki.', 409)
    if action == 'flee':
        b['log'].append('Wycofujesz się. Bez nagrody, ale w jednym kawałku.')
        finish_battle(s, 'fled')
        return
    enemy = b['enemies'][b['index']]
    if action == 'medkit':
        healed = medkit(s)
        b['log'].append(f'Apteczka przywraca {healed} HP.')
    else:
        if action == 'grenade':
            if s['inventory'].get('grenade', 0) < 1:
                fail('Nie masz granatu.')
            inventory_add(s, 'grenade', -1)
            damage = ITEMS['grenade']['damage']
        else:
            weapon = ITEMS.get(s['equipment']['weapon'], {})
            if action == 'attack' and weapon.get('uses_ammo'):
                if s['inventory'].get('ammo', 0) < 1:
                    fail('Brak nabojów. Użyj pięści, granatu albo wycofaj się.')
                inventory_add(s, 'ammo', -1)
            attack = BASE_ATTACK if action == 'unarmed' else stats(s)['attack']
            damage = max(1, attack + RNG.randint(-2, 3) - enemy['defense'])
        enemy['hp'] = max(0, enemy['hp'] - damage)
        label = 'Granat' if action == 'grenade' else 'Uderzasz pięścią' if action == 'unarmed' else 'Trafiasz'
        b['log'].append(f'{label}: {damage} obrażeń.')
    if enemy['hp'] == 0:
        b['log'].append(f"{enemy['name']} pada.")
        b['index'] += 1
        if b['index'] == len(b['enemies']):
            finish_battle(s, 'victory')
            return
        b['log'].append('Następny przeciwnik wkracza do walki.')
    else:
        damage = max(1, enemy['attack'] + RNG.randint(-2, 2) - stats(s)['defense'])
        s['hp'] = max(0, s['hp'] - damage)
        b['log'].append(f"{enemy['name']} zadaje {damage} obrażeń.")
        if s['hp'] == 0:
            b['log'].append('Tracisz przytomność. Po chwili odzyskujesz część sił.')
            finish_battle(s, 'defeat')
            return
    b['turn'] += 1
    b['log'] = b['log'][-12:]


def record_location(s, fix, expedition_id, seq):
    validate_fix(fix)
    e = s['expedition']
    if not e or not e['active'] or e['id'] != expedition_id:
        fail('Ta wyprawa nie jest aktywna.', 409)
    if seq <= e['seq']:
        return
    e['seq'] = seq
    if fix['timestamp'] <= e.get('last_seen', 0):
        return
    e['last_seen'] = fix['timestamp']
    s['location'] = fix
    last = e['last']
    if fix['accuracy'] > 35 or abs(fix['lat']) > 85:
        e['last'] = None
        return
    if last and fix['timestamp'] > last['timestamp'] and fix.get('demo', False) == last.get('demo', False):
        dt = fix['timestamp'] - last['timestamp']
        meters = distance(last, fix)
        threshold = max(10, (last['accuracy'] + fix['accuracy']) * .5)
        if meters < threshold and dt < 90:
            return  # Retain anchor, allowing real slow movement to accumulate.
        # Gaps can add only a plausible straight line, explicitly marked estimated.
        if meters >= threshold and meters / dt <= 3.5 and meters <= 3000:
            e['distance'] += meters
            if dt > 45:
                e['estimated'] += meters
            s['daily'][today()] = s['daily'].get(today(), 0) + meters
    e['last'] = fix
