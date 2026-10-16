import copy
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from app.db import Player, Receipt, Session, SessionLocal, engine
from app.main import app, digest

PASSWORD = 'przetrwanie-123!'


def auth(c, email='ocalały@example.com', mode='register', password=PASSWORD):
    token = c.get('/api/bootstrap').json()['csrf']
    c.headers.update({'Origin': 'http://testserver', 'X-CSRF-Token': token})
    r = c.post('/api/' + mode, json=dict(email=email, password=password, password_repeat=password, nickname='Wędrowiec'))
    if r.status_code == 200:
        c.headers['X-CSRF-Token'] = r.json()['csrf']
    return r


def me(c):
    r = c.get('/api/me')
    assert r.status_code == 200, r.text
    return r.json()['player']


def action(c, kind, key=None, **data):
    return c.post('/api/action', json=dict(key=key or str(uuid.uuid4()), action=kind, **data))


def fix(p=None, **extra):
    p = p or {'lat': 52.2297, 'lng': 21.0122}
    return dict(lat=p['lat'], lng=p['lng'], accuracy=5, timestamp=time.time(), demo=True, **extra)


def world(c):
    assert action(c, 'start_expedition').status_code == 200
    e = me(c)['expedition']
    assert action(c, 'location', expedition_id=e['id'], seq=1, fix=fix()).status_code == 200
    return me(c)['points']


def edit_state(fn):
    with SessionLocal() as db:
        p = db.scalar(select(Player))
        s = copy.deepcopy(p.state)
        fn(s)
        p.state = s
        db.commit()


def test_registration_session_refresh_login_logout(client):
    r = auth(client, '  OCALALY@EXAMPLE.COM ')
    assert r.status_code == 200
    assert r.json()['email'] == 'ocalaly@example.com'
    s = me(client)
    assert (s['level'], s['gold'], s['hp'], s['rank']) == (1, 100, 100, 'Neutralna')
    assert s['equipment'] == {'weapon': None, 'armor': None}
    assert s['nickname'] == 'Wędrowiec'
    assert 'HttpOnly' in r.headers['set-cookie'] and 'SameSite=lax' in r.headers['set-cookie']
    token = client.cookies.get('pustkowia')
    with SessionLocal() as db:
        assert db.get(Session, digest(token))
        p = db.scalar(select(Player))
        assert p.password.startswith('$argon2id$') and PASSWORD not in p.password
    with TestClient(app, base_url='http://testserver') as reopened:
        reopened.cookies.update(client.cookies)
        assert me(reopened) == s
    assert client.post('/api/logout', json={}).status_code == 200
    assert client.get('/api/me').status_code == 401
    assert auth(client, 'ocalaly@example.com', 'login').status_code == 200
    assert me(client)['gold'] == 100


def test_validation_unique_email_and_bad_login(client):
    assert auth(client, 'not-an-email').status_code == 400
    assert auth(client, password='short').status_code == 400
    assert auth(client, 'person@example.com').status_code == 200
    assert auth(client, 'PERSON@example.com').status_code == 409
    assert auth(client, 'person@example.com', 'login', 'wrong-password').status_code == 401


def test_csrf_expiration_and_unauthenticated(client):
    assert action(client, 'heal').status_code == 401
    auth(client)
    token = client.headers.pop('X-CSRF-Token')
    assert action(client, 'heal').status_code == 403
    client.headers['X-CSRF-Token'] = token
    client.headers['Origin'] = 'https://evil.example'
    assert action(client, 'heal').status_code == 403
    client.headers['Origin'] = 'http://testserver'
    with SessionLocal() as db:
        s = db.scalar(select(Session)); s.expires = time.time() - 1; db.commit()
    assert client.get('/api/me').status_code == 401


def test_login_rate_limit(client):
    for _ in range(10):
        assert auth(client, 'missing@example.com', 'login').status_code == 401
    assert auth(client, 'missing@example.com', 'login').status_code == 429


def test_world_stability_and_two_player_isolation(client):
    auth(client, 'first@example.com')
    points = world(client)
    assert len(points) == 9 and points[0]['type'] == 'city'
    assert 200 <= __import__('app.world', fromlist=['distance']).distance(fix(), points[0]) <= 500
    assert client.get('/api/me').json()['player']['points'] == points
    with TestClient(app, base_url='http://testserver') as other:
        auth(other, 'second@example.com'); world(other)
        assert action(other, 'inspect', point_id=points[0]['id'], fix=fix(points[0])).status_code == 404
        assert me(other)['gold'] == 100
    assert me(client)['points'] == points


def test_trade_atomic_idempotent_equipped_and_insufficient_gold(client):
    auth(client); city = world(client)[0]; f = fix(city); key = str(uuid.uuid4())
    action(client, 'equip', item='knife')
    assert action(client, 'buy', key, item='club', quantity=1, point_id=city['id'], fix=f).status_code == 200
    assert action(client, 'buy', key, item='club', quantity=1, point_id=city['id'], fix=f).status_code == 200
    assert me(client)['gold'] == 35 and me(client)['inventory']['club'] == 1
    assert action(client, 'buy', key, item='medkit', point_id=city['id'], fix=f).status_code == 409
    assert action(client, 'buy', item='pistol', point_id=city['id'], fix=f).status_code == 400
    assert action(client, 'sell', item='knife', point_id=city['id'], fix=f).status_code == 400
    assert action(client, 'equip', item='club').status_code == 200
    assert me(client)['stats']['attack'] == 18
    assert action(client, 'sell', item='knife', point_id=city['id'], fix=f).status_code == 200
    assert me(client)['gold'] == 48.2 and 'knife' not in me(client)['inventory']
    key = str(uuid.uuid4())
    for _ in range(2):
        assert action(client, 'sell', key, item='medkit', quantity=2, point_id=city['id'], fix=f).status_code == 200
    assert me(client)['gold'] == 68.2 and 'medkit' not in me(client)['inventory']
    assert action(client, 'unequip', slot='weapon').status_code == 200
    assert me(client)['stats']['attack'] == 6
    with SessionLocal() as db:
        for receipt in db.scalars(select(Receipt)):
            assert receipt.response == {'ok': True}  # No coordinate snapshots in receipt history.


@pytest.mark.parametrize('quantity',[0,-1,1.5,100,'2',True])
def test_invalid_quantities(client, quantity):
    auth(client)
    assert action(client, 'buy', item='medkit', quantity=quantity).status_code == 422


def test_location_range_age_accuracy_and_town_required(client):
    auth(client); points = world(client); city = points[0]
    assert action(client, 'buy', item='medkit', point_id=city['id'], fix=fix()).status_code == 403
    for field, value in [('timestamp',time.time()-60),('timestamp',time.time()+30),('accuracy',90)]:
        f = fix(city); f[field] = value
        assert action(client, 'inspect', point_id=city['id'], fix=f).status_code == 400
    f = fix(city); f['lat'] = 181
    assert action(client, 'inspect', point_id=city['id'], fix=f).status_code == 422
    assert action(client, 'buy', item='medkit', point_id=points[1]['id'], fix=fix(points[1])).status_code == 400


def test_persisted_encounter_battle_turn_heal_flee_and_exclusive(client):
    auth(client); p = world(client)[1]
    assert action(client, 'inspect', point_id=p['id'], fix=fix(p)).status_code == 200
    enemies = me(client)['points'][1]['encounter']
    action(client, 'inspect', point_id=p['id'], fix=fix(p))
    assert me(client)['points'][1]['encounter'] == enemies
    action(client, 'battle_start', point_id=p['id'], fix=fix(p))
    b = me(client)['battle']
    assert action(client, 'battle_start', point_id=p['id'], fix=fix(p)).status_code == 400
    assert action(client, 'equip', item='knife').status_code == 400
    key = str(uuid.uuid4())
    assert action(client, 'battle_action', key, battle_id=b['id'], turn=0).status_code == 200
    saved = me(client)
    action(client, 'battle_action', key, battle_id=b['id'], turn=0)
    assert me(client) == saved
    assert action(client, 'battle_action', battle_id=b['id'], turn=0).status_code == 409
    edit_state(lambda s: s.update(hp=30))
    b = me(client)['battle']
    action(client, 'battle_action', battle_id=b['id'], turn=b['turn'], move='medkit')
    after = me(client)
    assert 30 < after['hp'] < 75 and after['inventory']['medkit'] == 1
    b = after['battle']
    action(client, 'battle_action', battle_id=b['id'], turn=b['turn'], move='flee')
    s = me(client)
    assert s['battle'] is None and s['last_battle']['result'] == 'fled' and s['gold'] == 100


def prepare_easy_battle(client):
    auth(client); p = world(client)[1]
    action(client, 'equip', item='knife')
    action(client, 'equip', item='jacket')
    from app.catalog import ENEMIES
    def edit(s):
        s['points'][1]['encounter'] = [dict(kind='rat', **ENEMIES['rat'], max_hp=24)]
        s['xp'] = 95
    edit_state(edit)
    action(client, 'battle_start', point_id=p['id'], fix=fix(p))
    return p


def test_victory_rewards_level_cooldown_and_retry(client):
    p = prepare_easy_battle(client)
    for _ in range(10):
        b = me(client)['battle']
        if not b: break
        key = str(uuid.uuid4())
        assert action(client, 'battle_action', key, battle_id=b['id'], turn=b['turn']).status_code == 200
        assert action(client, 'battle_action', key, battle_id=b['id'], turn=b['turn']).status_code == 200
    s = me(client)
    assert s['battle'] is None and s['last_battle']['result'] == 'victory'
    assert s['gold'] == 112 and s['level'] == 2 and s['xp'] == 15 and s['hp'] == 112
    assert sum(s['last_battle']['rewards']['loot'].values()) >= 1
    assert action(client, 'battle_start', point_id=p['id'], fix=fix(p)).status_code == 400
    assert me(client) == s
    edit_state(lambda state: state['points'][1].update(cooldown_until=time.time()-1))
    assert action(client, 'inspect', point_id=p['id'], fix=fix(p)).status_code == 200
    assert me(client)['points'][1]['encounter']


def test_defeat_restores_hp_and_preserves_items(client):
    prepare_easy_battle(client)
    edit_state(lambda s: s.update(hp=1))
    before = me(client); b = before['battle']
    action(client, 'battle_action', battle_id=b['id'], turn=b['turn'])
    s = me(client)
    assert s['last_battle']['result'] == 'defeat' and s['hp'] == 40
    assert s['gold'] == 100 and s['inventory'] == before['inventory']
    assert s['points'][1]['cooldown_until'] > time.time()


def test_demo_disabled_on_api(client, monkeypatch):
    from app.config import settings
    auth(client); city = world(client)[0]
    monkeypatch.setattr(settings(), 'demo_enabled', False)
    assert action(client, 'inspect', point_id=city['id'], fix=fix(city)).status_code == 403


@pytest.mark.skipif(engine.dialect.name != 'postgresql', reason='Wymaga TEST_DATABASE_URL z PostgreSQL.')
def test_concurrent_purchase_same_key(client):
    auth(client); city = world(client)[0]; key = str(uuid.uuid4()); f = fix(city)
    cookies, headers = dict(client.cookies), dict(client.headers)
    def purchase(_):
        with TestClient(app, base_url='http://testserver') as c:
            c.cookies.update(cookies); c.headers.update(headers)
            return action(c, 'buy', key, item='medkit', quantity=2, point_id=city['id'], fix=f).status_code
    with ThreadPoolExecutor(max_workers=4) as pool:
        assert list(pool.map(purchase, range(4))) == [200]*4
    assert me(client)['gold'] == 50 and me(client)['inventory']['medkit'] == 4


@pytest.mark.skipif(engine.dialect.name != 'postgresql', reason='Wymaga PostgreSQL.')
def test_concurrent_distinct_purchases_cannot_overspend(client):
    auth(client); city = world(client)[0]; f = fix(city)
    cookies, headers = dict(client.cookies), dict(client.headers)
    def purchase(_):
        with TestClient(app, base_url='http://testserver') as c:
            c.cookies.update(cookies); c.headers.update(headers)
            return action(c, 'buy', item='club', quantity=1, point_id=city['id'], fix=f).status_code
    with ThreadPoolExecutor(max_workers=4) as pool:
        assert sorted(pool.map(purchase, range(4))) == [200, 400, 400, 400]
    assert me(client)['gold'] == 35 and me(client)['inventory']['club'] == 1


@pytest.mark.skipif(engine.dialect.name != 'postgresql', reason='Wymaga PostgreSQL.')
def test_concurrent_final_attack_rewards_once(client):
    prepare_easy_battle(client)
    edit_state(lambda s: s['battle']['enemies'][0].update(hp=1))
    b = me(client)['battle']
    cookies, headers = dict(client.cookies), dict(client.headers)
    def attack(_):
        with TestClient(app, base_url='http://testserver') as c:
            c.cookies.update(cookies); c.headers.update(headers)
            return action(c, 'battle_action', battle_id=b['id'], turn=b['turn']).status_code
    with ThreadPoolExecutor(max_workers=4) as pool:
        assert sorted(pool.map(attack, range(4))) == [200, 409, 409, 409]
    s = me(client)
    assert s['gold'] == 112 and s['level'] == 2
