import os
import subprocess
import sys
from pathlib import Path
from sqlalchemy import MetaData, Table, create_engine, inspect, select


def test_alembic_upgrade_idempotent(tmp_path):
    url = 'sqlite:///' + str(tmp_path / 'migration.db').replace('\\', '/')
    env = dict(os.environ, DATABASE_URL=url, PYTHONPATH='backend')
    for _ in range(2):
        result = subprocess.run([sys.executable, '-m', 'alembic', 'upgrade', 'head'], env=env, capture_output=True, text=True)
        assert result.returncode == 0, result.stderr
    db = create_engine(url)
    assert {'players', 'sessions', 'receipts', 'login_buckets', 'alembic_version'} <= set(inspect(db).get_table_names())
    db.dispose()


def test_spa_and_unknown_api(client):
    if not Path('dist/index.html').exists():
        import pytest
        pytest.skip('Uruchom npm run build, aby sprawdzić serwowanie frontendu.')
    assert client.get('/').status_code == 200
    assert 'Pustkowia' in client.get('/').text
    assert client.get('/manifest.webmanifest').json()['lang'] == 'pl'
    assert client.get('/api/nonexistent').status_code == 404
    assert client.get('/api/health').json() == {'status': 'ok'}


def test_deployment_migration_grants_pack_to_existing_account_once(tmp_path):
    from app.catalog import ITEMS, new_state
    url = 'sqlite:///' + str(tmp_path / 'existing-player.db').replace('\\', '/')
    env = dict(os.environ, DATABASE_URL=url, PYTHONPATH='backend')
    initial = subprocess.run([sys.executable, '-m', 'alembic', 'upgrade', '0001'], env=env, capture_output=True, text=True)
    assert initial.returncode == 0, initial.stderr
    db = create_engine(url)
    players = Table('players', MetaData(), autoload_with=db)
    with db.begin() as connection:
        connection.execute(players.insert().values(id='existing-owner', email='owner@example.com', password='test-only', state=new_state('Marcin')))
    for _ in range(2):
        upgraded = subprocess.run([sys.executable, '-m', 'alembic', 'upgrade', 'head'], env=env, capture_output=True, text=True)
        assert upgraded.returncode == 0, upgraded.stderr
    with db.connect() as connection:
        state = connection.execute(select(players.c.state)).scalar_one()
    assert set(state['inventory']) == set(ITEMS)
    assert state['inventory']['ammo'] == 100 and state['inventory']['grenade'] == 5
    assert state['inventory']['knife'] == 2 and state['inventory']['medkit'] == 7
    db.dispose()
