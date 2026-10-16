import os
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

Path('test-results').mkdir(exist_ok=True)
test_url = os.environ.get('TEST_DATABASE_URL', 'sqlite:///test-results/integration.db')
if not test_url.startswith('sqlite') and not test_url.split('?')[0].endswith('_test'):
    raise RuntimeError('TEST_DATABASE_URL musi wskazywać dedykowaną bazę z nazwą kończącą się _test.')
os.environ.update(DATABASE_URL=test_url, ENVIRONMENT='development', APP_ORIGIN='http://testserver',
                  WORLD_SOURCE='demonstration', DEMO_ENABLED='true', SECRET_KEY='test-only-strong-secret-key-123456789')
from app.db import Base, engine
from app.main import app


@pytest.fixture(autouse=True)
def clean_db():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    yield


@pytest.fixture
def client():
    with TestClient(app, base_url='http://testserver') as c:
        yield c
