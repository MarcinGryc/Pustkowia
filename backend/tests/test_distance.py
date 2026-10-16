import time
import uuid
import pytest
from fastapi import HTTPException
from app.catalog import new_state
from app.game import record_location, today
from app.world import distance, offset


def setup():
    s = new_state()
    s['expedition'] = dict(id=str(uuid.uuid4()), active=True, distance=0, estimated=0, seq=0, last=None)
    return s, s['expedition']


def test_distance_drift_speed_gaps_deduplication():
    s, e = setup(); now = time.time(); p = dict(lat=52, lng=21, accuracy=5, timestamp=now-30, demo=False)
    record_location(s, p, e['id'], 1)
    q = dict(p, **offset(p, 2, 0), timestamp=now-25)
    record_location(s, q, e['id'], 2)
    assert e['distance'] == 0
    q = dict(p, **offset(p, 25, 0), timestamp=now-10)
    record_location(s, q, e['id'], 3)
    assert 24 < e['distance'] < 26
    record_location(s, q, e['id'], 3)
    assert 24 < e['distance'] < 26
    # A repeated or out-of-order timestamp must not move the anchor backwards,
    # even when a client gives it a fresh sequence number.
    anchor = e['last'].copy()
    record_location(s, p, e['id'], 4)
    assert e['last'] == anchor and e['distance'] < 26
    jump = dict(p, **offset(p, 900, 0), timestamp=now)
    record_location(s, jump, e['id'], 5)
    assert e['distance'] < 26
    e['last'] = dict(p, timestamp=now-120)
    e['last_seen'] = now - 1
    gap = dict(p, **offset(p, 100, 0), timestamp=now)
    record_location(s, gap, e['id'], 6)
    assert 99 < e['estimated'] < 101 and 124 < e['distance'] < 126
    assert s['daily'][today()] == e['distance']


def test_weak_accuracy_and_inactive_expedition():
    s, e = setup(); p = dict(lat=52, lng=21, accuracy=40, timestamp=time.time(), demo=False)
    record_location(s, p, e['id'], 1)
    assert e['last'] is None and e['distance'] == 0
    e['active'] = False
    with pytest.raises(HTTPException): record_location(s, p, e['id'], 2)


def test_distance_boundary_and_warsaw_timezone(monkeypatch):
    assert distance({'lat':0,'lng':0},{'lat':0,'lng':0}) == 0
    from datetime import datetime, timezone
    class Clock:
        @staticmethod
        def now(tz): return datetime(2026, 10, 14, 22, 30, tzinfo=timezone.utc).astimezone(tz)
    monkeypatch.setattr('app.game.datetime', Clock)
    assert today() == '2026-10-15'
