import copy
import importlib.util
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from app.catalog import ITEMS, SETTLEMENTS, SHOP, sell_price
from app.db import Player, SessionLocal, engine
from app.game import refresh_state
from app.main import app
from test_api import action, auth, edit_state, fix, me, world


def fight(client, weapon, ammo=5, grenades=2):
    auth(client)
    spot = world(client)[1]
    def setup(s):
        s['inventory'].update({weapon: 1, 'ammo': ammo, 'grenade': grenades})
        s['equipment']['weapon'] = weapon
        s['points'][1]['encounter'] = [dict(kind='mutant', name='Mutant', icon='mutant',
            hp=1000, max_hp=1000, attack=1, defense=0, gold=55, xp=80)]
    edit_state(setup)
    assert action(client, 'battle_start', point_id=spot['id'], fix=fix(spot)).status_code == 200


@pytest.mark.parametrize('weapon', ['pistol', 'revolver', 'ak47'])
def test_firearms_share_ammo_consume_one_and_retry_once(client, weapon):
    fight(client, weapon, ammo=1)
    b = me(client)['battle']
    key = str(uuid.uuid4())
    for _ in range(2):
        assert action(client, 'battle_action', key, battle_id=b['id'], turn=b['turn']).status_code == 200
    after = me(client)
    assert not after['inventory'].get('ammo') and after['battle']['turn'] == 1
    assert after['battle']['enemies'][0]['hp'] < 1000
    b = after['battle']
    assert action(client, 'battle_action', battle_id=b['id'], turn=b['turn']).status_code == 400
    assert me(client) == after  # A rejected shot spends neither a turn nor HP.
    assert action(client, 'battle_action', battle_id=b['id'], turn=b['turn'], move='unarmed').status_code == 200
    assert 1 <= b['enemies'][0]['hp'] - me(client)['battle']['enemies'][0]['hp'] <= 9


@pytest.mark.parametrize('weapon', ['knife', 'club', 'machete', 'chainsaw'])
def test_melee_does_not_consume_ammo(client, weapon):
    fight(client, weapon)
    b = me(client)['battle']
    assert action(client, 'battle_action', battle_id=b['id'], turn=b['turn']).status_code == 200
    assert me(client)['inventory']['ammo'] == 5


def test_grenade_fixed_damage_ignores_defense_and_is_consumed(client):
    fight(client, 'pistol', ammo=0, grenades=1)
    edit_state(lambda s: s['battle']['enemies'][0].update(hp=60, defense=999))
    b = me(client)['battle']
    key = str(uuid.uuid4())
    for _ in range(2):
        assert action(client, 'battle_action', key, battle_id=b['id'], turn=b['turn'], move='grenade').status_code == 200
    s = me(client)
    assert s['battle']['enemies'][0]['hp'] == 15 and s['battle']['turn'] == 1
    assert not s['inventory'].get('grenade') and not s['inventory'].get('ammo')
    b = s['battle']
    assert action(client, 'battle_action', battle_id=b['id'], turn=b['turn'], move='grenade').status_code == 400
    assert me(client) == s


def test_medkit_does_not_fire_equipped_gun(client):
    fight(client, 'ak47')
    edit_state(lambda s: s.update(hp=20))
    b = me(client)['battle']
    assert action(client, 'battle_action', battle_id=b['id'], turn=b['turn'], move='medkit').status_code == 200
    assert me(client)['inventory']['ammo'] == 5


def test_grenade_can_win_and_award_rewards_once(client):
    fight(client, 'pistol', ammo=0)
    edit_state(lambda s: s['battle']['enemies'][0].update(hp=30))
    b = me(client)['battle']
    key = str(uuid.uuid4())
    for _ in range(2):
        assert action(client, 'battle_action', key, battle_id=b['id'], turn=b['turn'], move='grenade').status_code == 200
    s = me(client)
    assert s['battle'] is None and s['last_battle']['result'] == 'victory'
    assert s['gold'] == 155 and s['xp'] == 80


def test_world_contains_all_settlement_types_and_six_combat_sites(client):
    auth(client)
    points = world(client)
    cities = [p for p in points if p['type'] == 'city']
    assert {p['settlement'] for p in cities} == set(SETTLEMENTS)
    assert {p['name'] for p in cities} == {'Obóz', 'Osada', 'Miasto'}
    assert len([p for p in points if p['type'] == 'spot']) == 6
    config = client.get('/api/bootstrap').json()
    assert config['settlements'] == SETTLEMENTS
    assert set(config['catalog']) == set(ITEMS) and len(ITEMS) == 18
    assert set(SHOP) == set(ITEMS) - {'scrap', 'electronics'}


@pytest.mark.parametrize('kind,item,other', [
    ('camp', 'knife', 'jacket'), ('settlement', 'jacket', 'knife'), ('city', 'ammo', 'knife')])
def test_settlement_bonus_exact_ten_percent_quantity_and_retry(client, kind, item, other):
    auth(client)
    city = next(p for p in world(client) if p.get('settlement') == kind)
    edit_state(lambda s: s['inventory'].update({item: 3, other: 1}))
    f, key = fix(city), str(uuid.uuid4())
    expected = round(100 + ITEMS[item]['sell'] * 1.1 * 3, 1)
    for _ in range(2):
        assert action(client, 'sell', key, item=item, quantity=3, point_id=city['id'], fix=f).status_code == 200
    assert me(client)['gold'] == expected
    assert action(client, 'sell', item=other, point_id=city['id'], fix=f).status_code == 200
    assert me(client)['gold'] == round(expected + ITEMS[other]['sell'], 1)
    assert sell_price(item, city) == round(ITEMS[item]['sell'] * 1.1, 1)


def test_new_items_can_be_bought_and_all_armors_change_defense(client):
    auth(client)
    city = world(client)[0]
    edit_state(lambda s: s.update(gold=10000))
    for item in SHOP:
        before = me(client)['gold']
        assert action(client, 'buy', item=item, point_id=city['id'], fix=fix(city)).status_code == 200
        assert me(client)['gold'] == before - ITEMS[item]['price']
        if ITEMS[item]['kind'] in ('weapon', 'armor'):
            assert action(client, 'equip', item=item).status_code == 200
            s = me(client)
            if ITEMS[item]['kind'] == 'armor':
                assert s['stats']['defense'] == ITEMS[item]['defense']
            else:
                assert s['stats']['attack'] == 6 + ITEMS[item]['attack']


def pack_migration():
    path = Path('backend/migrations/versions/0002_content_pack.py')
    spec = importlib.util.spec_from_file_location('content_pack_migration', path)
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)
    return migration


def test_pack_is_targeted_additive_and_one_time(client):
    auth(client, 'owner@example.com')
    action(client, 'nickname', nickname='Marcin')
    with TestClient(app, base_url='http://testserver') as other:
        auth(other, 'other@example.com')
    pack = pack_migration()
    before = me(client)
    with engine.begin() as connection:
        assert pack.grant_pack(connection) is True
        assert pack.grant_pack(connection) is False
    s = me(client)
    assert set(s['inventory']) == set(ITEMS)
    assert s['inventory']['ammo'] == 100 and s['inventory']['grenade'] == 5
    assert s['inventory']['knife'] == before['inventory']['knife'] + 1
    assert s['gold'] == before['gold'] and s['equipment'] == before['equipment']
    with SessionLocal() as db:
        other = db.scalar(select(Player).where(Player.email == 'other@example.com'))
        assert set(other.state['inventory']) == {'knife', 'jacket', 'medkit'}


def test_pack_does_not_guess_between_duplicate_nicknames(client):
    auth(client)
    action(client, 'nickname', nickname='Marcin')
    with TestClient(app, base_url='http://testserver') as other:
        auth(other, 'other@example.com')
        action(other, 'nickname', nickname='marcin')
    with engine.begin() as connection:
        assert pack_migration().grant_pack(connection) is False
    assert 'ammo' not in me(client)['inventory']


@pytest.mark.skipif(engine.dialect.name != 'postgresql', reason='Wymaga PostgreSQL.')
def test_concurrent_shots_cannot_spend_one_bullet_twice(client):
    fight(client, 'ak47', ammo=1)
    b = me(client)['battle']
    cookies, headers = dict(client.cookies), dict(client.headers)
    def shoot(_):
        with TestClient(app, base_url='http://testserver') as c:
            c.cookies.update(cookies)
            c.headers.update(headers)
            return action(c, 'battle_action', battle_id=b['id'], turn=b['turn']).status_code
    with ThreadPoolExecutor(max_workers=4) as pool:
        assert sorted(pool.map(shoot, range(4))) == [200, 409, 409, 409]
    assert not me(client)['inventory'].get('ammo') and me(client)['battle']['turn'] == 1
