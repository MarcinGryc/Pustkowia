import os
import subprocess
import sys
from pathlib import Path
from sqlalchemy import create_engine, inspect


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
