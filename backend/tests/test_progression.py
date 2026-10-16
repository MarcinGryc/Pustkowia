import copy
import time
import uuid

import pytest
from app.catalog import max_hp, new_state, stats
from app.game import finish_battle, refresh_state
from app.world import distance
from test_api import PASSWORD, action, auth, edit_state, fix, me, prepare_easy_battle, world


def test_nickname_validation_persistence_and_old_account(client):
    token = client.get('/api/bootstrap').json()['csrf']
    client.headers.update({'Origin': 'http://testserver', 'X-CSRF-Token': token})
    for nickname in [None, '', ' ', 'A', '<script>', 'x' * 25]:
        response = client.post('/api/register', json=dict(email='test@example.com', password=PASSWORD,
                               password_repeat=PASSWORD, nickname=nickname))
        assert response.status_code in (400, 422)
    assert auth(client).status_code == 200
    assert action(client, 'nickname', nickname='  Łowca_17  ').status_code == 200
    assert me(client)['nickname'] == 'Łowca_17'
    assert action(client, 'nickname', nickname='<script>').status_code == 400
    # Simulate a save made before nicknames and chosen bonuses existed.
    def legacy(s):
        for key in ('nickname', 'upgrades', 'upgrade_points', 'regen_at'):
            s.pop(key, None)
        s.update(level=4, hp=120)
    edit_state(legacy)
    s = me(client)
    assert s['nickname'] is None and s['max_hp'] == 136 and s['hp'] == 120
    assert 'upgrades' not in s and 'upgrade_points' not in s
    assert action(client, 'nickname', nickname='Weteran').status_code == 200
    assert auth(client, mode='login').json()['player']['nickname'] == 'Weteran'


def test_search_moves_world_and_deduplicates_retries(client):
    auth(client)
    assert action(client, 'search', fix=fix()).status_code == 400
    old = world(client)
    expedition = me(client)['expedition']
    f = fix({'lat': 48.8566, 'lng': 2.3522})
    key = str(uuid.uuid4())
    assert action(client, 'search', key, fix=f).status_code == 200
    found = me(client)
    assert len(found['points']) == 9
    assert not {p['id'] for p in old} & {p['id'] for p in found['points']}
    assert all(100 <= distance(f, p) <= 1000 for p in found['points'])
    assert 200 <= distance(f, found['points'][0]) <= 500
    assert found['expedition'] == expedition
    assert action(client, 'search', key, fix=f).status_code == 200
    assert me(client)['points'] == found['points']
    stale = dict(f, timestamp=time.time() - 100)
    assert action(client, 'search', fix=stale).status_code == 400
    assert me(client)['points'] == found['points']


def test_search_preserves_nearby_cooldown_and_blocks_during_combat(client, monkeypatch):
    prepare_easy_battle(client)
    assert action(client, 'search', fix=fix()).status_code == 400
    assert action(client, 'end_expedition').status_code == 400
    b = me(client)['battle']
    action(client, 'battle_action', battle_id=b['id'], turn=b['turn'], move='flee')
    old = me(client)['points']
    generated = copy.deepcopy(old)
    for p in generated:
        p.update(id=str(uuid.uuid4()), cooldown_until=0, encounter=None)
    monkeypatch.setattr('app.main.generate_world', lambda _: copy.deepcopy(generated))
    assert action(client, 'search', fix=fix()).status_code == 200
    s = me(client)
    assert s['points'][1]['cooldown_until'] == old[1]['cooldown_until']


@pytest.mark.parametrize('bonus_hp,hp,expected_hp', [(0, 60, 96), (5, 85, 116), (5, 105, 136)])
def test_choice_system_save_converts_once_without_losing_level_or_wounds(client, bonus_hp, hp, expected_hp):
    auth(client)
    edit_state(lambda s: s.update(level=4, xp=25, hp=hp, upgrades=dict(attack=1, defense=1, hp=bonus_hp), upgrade_points=2))
    for _ in range(2):
        s = me(client)
        assert s['level'] == 4 and s['xp'] == 25 and s['max_hp'] == 136
        assert s['hp'] == expected_hp
        assert s['stats'] == dict(attack=6, defense=0)
        assert 'upgrades' not in s and 'upgrade_points' not in s
    saved = auth(client, mode='login').json()['player']
    assert saved['hp'] == expected_hp and saved['max_hp'] == 136


def test_upgrade_choice_endpoint_removed(client):
    auth(client)
    assert action(client, 'upgrade', upgrade='attack').status_code == 422


def test_multiple_level_rewards_increase_max_hp_and_heal():
    s = new_state('Test')
    s['points'] = [dict(id='spot', cooldown_until=0, encounter=None)]
    s['battle'] = dict(id='battle', point_id='spot', enemies=[dict(gold=10, xp=650)], log=[])
    s.update(hp=20)
    finish_battle(s, 'victory')
    assert s['level'] == 4 and s['xp'] == 50
    assert s['last_battle']['rewards']['levels'] == 3
    assert s['hp'] == max_hp(s) == 136 and stats(s) == dict(attack=6, defense=0)


def test_regen_whole_minutes_cap_and_no_banked_healing():
    s = new_state('Test')
    s.update(hp=50, regen_at=1000)
    refresh_state(s, now=1059)
    assert s['hp'] == 50
    refresh_state(s, now=1060)
    assert s['hp'] == 51 and s['regen_at'] == 1060
    refresh_state(s, now=1185)
    assert s['hp'] == 53 and s['regen_at'] == 1180
    refresh_state(s, now=10000)
    assert s['hp'] == 100
    refresh_state(s, now=20000)
    s['hp'] = 50
    refresh_state(s, now=20001)
    assert s['hp'] == 50


def test_regen_persists_offline_and_medkit_restarts_minute(client, monkeypatch):
    auth(client)
    now = time.time()
    monkeypatch.setattr('app.game.time.time', lambda: now)
    edit_state(lambda s: s.update(hp=20, regen_at=now - 125))
    assert me(client)['hp'] == 22
    assert me(client)['hp'] == 22  # Refresh cannot grant healing twice.
    assert action(client, 'heal').status_code == 200
    assert me(client)['hp'] == 67
    now += 59
    assert me(client)['hp'] == 67
    now += 1
    assert me(client)['hp'] == 68
    now += 3600
    assert auth(client, mode='login').json()['player']['hp'] == 100


def test_no_regen_during_battle_or_immediately_after(client, monkeypatch):
    prepare_easy_battle(client)
    now = time.time()
    monkeypatch.setattr('app.game.time.time', lambda: now)
    edit_state(lambda s: s.update(hp=20, regen_at=now - 3600))
    assert me(client)['hp'] == 20
    b = me(client)['battle']
    action(client, 'battle_action', battle_id=b['id'], turn=b['turn'], move='flee')
    assert me(client)['hp'] == 20
    now += 60
    assert me(client)['hp'] == 21
