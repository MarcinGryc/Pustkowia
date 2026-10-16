import copy
import hashlib
import hmac
import json
import secrets
import time
import uuid
from pathlib import Path
from typing import Literal
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError
from email_validator import EmailNotValidError, validate_email
from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import delete, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session as DBSession
from .catalog import ITEMS, SHOP, SETTLEMENTS, new_state, sell_price
from .config import settings
from .db import LoginBucket, Player, Receipt, Session, engine, get_db
from .game import (battle_action, encounter, fail, inventory_add, medkit,
                   point_access, public_state, record_location, refresh_state, start_battle, validate_fix)
from .world import distance, generate_world

app = FastAPI(title='Pustkowia', docs_url='/api/docs', openapi_url='/api/openapi.json')
cfg = settings()
ph = PasswordHasher()
DUMMY_HASH = ph.hash(secrets.token_urlsafe(24))
COOKIE = '__Host-pustkowia' if cfg.production else 'pustkowia'


@app.middleware('http')
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['Permissions-Policy'] = 'geolocation=(self), screen-wake-lock=(self)'
    if request.url.path.startswith('/api'):
        response.headers['Cache-Control'] = 'no-store'
    if cfg.production:
        response.headers['Strict-Transport-Security'] = 'max-age=31536000'
    return response


@app.exception_handler(HTTPException)
async def http_error(request, exc):
    return JSONResponse({'error': exc.detail}, status_code=exc.status_code, headers=exc.headers)


@app.exception_handler(RequestValidationError)
async def validation_error(request, exc):
    return JSONResponse({'error': 'Nieprawidłowe dane. Sprawdź wymagane pola i zakresy wartości.'}, status_code=422)


@app.exception_handler(Exception)
async def unexpected_error(request, exc):
    # No request body, query parameters or coordinates in application error logs.
    import logging
    logging.getLogger('pustkowia').error('Błąd serwera: %s', type(exc).__name__)
    return JSONResponse({'error': 'Serwer nie może teraz wykonać operacji. Spróbuj ponownie.'}, status_code=500)


class Credentials(BaseModel):
    email: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=1, max_length=128)
    password_repeat: str | None = Field(default=None, max_length=128)
    nickname: str | None = Field(default=None, max_length=24)


class Fix(BaseModel):
    model_config = ConfigDict(allow_inf_nan=False)
    lat: float = Field(ge=-90, le=90)
    lng: float = Field(ge=-180, le=180)
    accuracy: float = Field(gt=0, le=100000)
    timestamp: float = Field(gt=0)
    demo: bool = False


class Action(BaseModel):
    model_config = ConfigDict(extra='forbid')
    key: uuid.UUID
    action: Literal['equip', 'unequip', 'heal', 'buy', 'sell', 'start_expedition', 'end_expedition', 'location', 'search', 'inspect', 'battle_start', 'battle_action', 'nickname']
    nickname: str | None = Field(default=None, max_length=24)
    item: str | None = Field(default=None, max_length=40)
    quantity: int = Field(default=1, ge=1, le=99, strict=True)
    slot: Literal['weapon', 'armor'] | None = None
    point_id: uuid.UUID | None = None
    fix: Fix | None = None
    expedition_id: uuid.UUID | None = None
    seq: int = Field(default=0, ge=0, le=9007199254740991, strict=True)
    battle_id: uuid.UUID | None = None
    turn: int = Field(default=0, ge=0, le=1000000, strict=True)
    move: Literal['attack', 'unarmed', 'grenade', 'medkit', 'flee'] = 'attack'


def digest(value):
    return hmac.new(cfg.secret_key.encode(), value.encode(), hashlib.sha256).hexdigest()


def csrf(request: Request):
    if request.headers.get('origin') != cfg.app_origin.rstrip('/'):
        fail('Nieprawidłowe źródło żądania. Odśwież stronę.', 403)
    cookie = request.cookies.get('pustkowia_csrf', '')
    header = request.headers.get('x-csrf-token', '')
    if not cookie or not hmac.compare_digest(cookie, header):
        fail('Sesja formularza wygasła. Odśwież stronę.', 403)
    return header


def current(request: Request, db: DBSession = Depends(get_db)):
    token = request.cookies.get(COOKIE, '')
    session = db.get(Session, digest(token)) if token else None
    if not session or session.expires <= time.time():
        fail('Zaloguj się, aby kontynuować.', 401)
    if request.method not in ('GET', 'HEAD'):
        if not hmac.compare_digest(csrf(request), session.csrf):
            fail('Sesja formularza wygasła. Odśwież stronę.', 403)
    return session


def set_csrf(response, value):
    response.set_cookie('pustkowia_csrf', value, max_age=cfg.session_days * 86400,
                        secure=cfg.production, httponly=True, samesite='lax', path='/')


def open_session(db, response, player):
    state = copy.deepcopy(player.state)
    refresh_state(state)
    player.state = state
    token, csrf_token = secrets.token_urlsafe(32), secrets.token_hex(24)
    db.add(Session(token=digest(token), player_id=player.id, csrf=csrf_token,
                   expires=time.time() + cfg.session_days * 86400))
    db.commit()
    response.set_cookie(COOKIE, token, max_age=cfg.session_days * 86400,
                        secure=cfg.production, httponly=True, samesite='lax', path='/')
    set_csrf(response, csrf_token)
    return {'player': public_state(player.state), 'csrf': csrf_token, 'email': player.email}


def normalize_email(email):
    try:
        return validate_email(email.strip(), check_deliverability=False).normalized.casefold()
    except EmailNotValidError:
        fail('Podaj poprawny adres e-mail.')


def normalize_nickname(value):
    value = (value or '').strip()
    if not 2 <= len(value) <= 24 or not all(c.isalnum() or c in ' _-' for c in value):
        fail('Nick musi mieć 2–24 znaki: litery, cyfry, spacje, _ lub -.')
    return value


def rate_limit(db, request, email):
    """Atomic DB-backed buckets, shared by workers. Do not trust forwarded client IP headers."""
    now = time.time()
    db.execute(delete(LoginBucket).where(LoginBucket.expires < now))
    for value, limit in [(f'email:{email}', 10), (f'ip:{request.client.host if request.client else "unknown"}', 60)]:
        key = digest(f'{int(now // 900)}:{value}')
        dialect = engine.dialect.name
        if dialect == 'postgresql':
            from sqlalchemy.dialects.postgresql import insert
        else:
            from sqlalchemy.dialects.sqlite import insert
        statement = insert(LoginBucket).values(key=key, attempts=1, expires=(int(now // 900) + 1) * 900)
        statement = statement.on_conflict_do_update(index_elements=['key'], set_={'attempts': LoginBucket.attempts + 1}).returning(LoginBucket.attempts)
        count = db.execute(statement).scalar_one()
        if count > limit:
            db.commit()
            fail('Zbyt wiele prób. Spróbuj ponownie za 15 minut.', 429)
    db.commit()


@app.get('/api/bootstrap')
def bootstrap(request: Request, response: Response, db: DBSession = Depends(get_db)):
    token = request.cookies.get(COOKIE, '')
    session = db.get(Session, digest(token)) if token else None
    csrf_token = session.csrf if session and session.expires > time.time() else secrets.token_hex(24)
    set_csrf(response, csrf_token)
    return dict(csrf=csrf_token, demo_enabled=cfg.demo_enabled, interaction_radius=cfg.interaction_radius_m,
                max_accuracy=cfg.max_accuracy_m, location_max_age=cfg.location_max_age_s,
                map_style=cfg.map_style_url, map_tiles=cfg.map_tiles_url, map_attribution=cfg.map_attribution,
                catalog=ITEMS, shop=SHOP, settlements=SETTLEMENTS)


@app.post('/api/register')
def register(body: Credentials, request: Request, response: Response, db: DBSession = Depends(get_db)):
    csrf(request)
    email = normalize_email(body.email)
    rate_limit(db, request, email)
    if len(body.password) < 10:
        fail('Hasło musi mieć co najmniej 10 znaków.')
    if body.password != body.password_repeat:
        fail('Hasła nie są takie same.')
    p = Player(email=email, password=ph.hash(body.password), state=new_state(normalize_nickname(body.nickname)))
    db.add(p)
    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        fail('Nie można utworzyć konta z tym adresem. Spróbuj się zalogować.', 409)
    return open_session(db, response, p)


@app.post('/api/login')
def login(body: Credentials, request: Request, response: Response, db: DBSession = Depends(get_db)):
    csrf(request)
    email = normalize_email(body.email)
    rate_limit(db, request, email)
    p = db.scalar(select(Player).where(Player.email == email).with_for_update())
    try:
        ph.verify(p.password if p else DUMMY_HASH, body.password)
        if not p:
            raise VerificationError()
    except (VerificationError, InvalidHashError):
        fail('Nieprawidłowy e-mail lub hasło.', 401)
    db.execute(delete(Session).where(Session.expires < time.time()))
    old = request.cookies.get(COOKIE)
    if old:
        db.execute(delete(Session).where(Session.token == digest(old)))
    return open_session(db, response, p)


@app.post('/api/logout')
def logout(response: Response, session=Depends(current), db: DBSession = Depends(get_db)):
    db.delete(session)
    db.commit()
    response.delete_cookie(COOKIE, path='/', secure=cfg.production, httponly=True, samesite='lax')
    response.delete_cookie('pustkowia_csrf', path='/')
    return {'ok': True}


@app.get('/api/me')
def me(session=Depends(current), db: DBSession = Depends(get_db)):
    p = db.scalar(select(Player).where(Player.id == session.player_id).with_for_update())
    s = copy.deepcopy(p.state)
    refresh_state(s)
    if s != p.state:
        p.state = s
        db.commit()
    return {'player': public_state(s), 'email': p.email}


@app.post('/api/action')
def action(body: Action, session=Depends(current), db: DBSession = Depends(get_db)):
    # One row lock serializes every change to a player's aggregate, including all rewards.
    p = db.scalar(select(Player).where(Player.id == session.player_id).with_for_update())
    fingerprint = hashlib.sha256(json.dumps(body.model_dump(mode='json', exclude={'key'}), sort_keys=True).encode()).hexdigest()
    receipt = db.scalar(select(Receipt).where(Receipt.player_id == p.id, Receipt.key == str(body.key))) if body.action != 'location' else None
    if receipt:
        if receipt.fingerprint != fingerprint:
            fail('Identyfikator żądania został już użyty z innymi danymi.', 409)
        return receipt.response
    s = copy.deepcopy(p.state)
    refresh_state(s)
    kind = body.action
    fix = body.fix.model_dump() if body.fix else None
    if kind in ('buy', 'sell', 'inspect', 'battle_start'):
        if not fix or not body.point_id:
            fail('Wymagane miejsce i aktualna lokalizacja.')
        point = point_access(s, str(body.point_id), fix)
    if kind in ('equip', 'unequip', 'heal', 'buy', 'sell', 'search', 'end_expedition') and s['battle']:
        fail('Dokończ aktywną walkę. Apteczkę użyj w ekranie walki.')
    if kind in ('equip', 'buy', 'sell') and body.item not in ITEMS:
        fail('Nieznany przedmiot.')
    if kind == 'equip':
        item = ITEMS[body.item]
        if item['kind'] not in ('weapon', 'armor') or not s['inventory'].get(body.item):
            fail('Nie możesz założyć tego przedmiotu.')
        s['equipment'][item['kind']] = body.item
    elif kind == 'unequip':
        if not body.slot:
            fail('Wybierz slot wyposażenia.')
        s['equipment'][body.slot] = None
    elif kind == 'heal':
        medkit(s)
    elif kind == 'nickname':
        s['nickname'] = normalize_nickname(body.nickname)
    elif kind in ('buy', 'sell'):
        if point['type'] != 'city':
            fail('Handel jest dostępny wyłącznie w osadzie.')
        if kind == 'buy':
            if body.item not in SHOP:
                fail('Ten przedmiot nie jest na sprzedaż.')
            cost = ITEMS[body.item]['price'] * body.quantity
            if s['gold'] < cost:
                fail('Masz za mało złota.')
            if s['inventory'].get(body.item, 0) + body.quantity > 9999:
                fail('Osiągnięto limit przedmiotu.')
            s['gold'] -= cost
            inventory_add(s, body.item, body.quantity)
        else:
            if body.item in s['equipment'].values():
                fail('Najpierw zdejmij ten przedmiot.')
            if s['inventory'].get(body.item, 0) < body.quantity:
                fail('Nie masz tylu przedmiotów.')
            inventory_add(s, body.item, -body.quantity)
            s['gold'] = round(s['gold'] + sell_price(body.item, point) * body.quantity, 1)
    elif kind == 'start_expedition':
        if not s['expedition'] or not s['expedition']['active']:
            s['expedition'] = dict(id=str(uuid.uuid4()), active=True, distance=0, estimated=0, seq=0, last=None)
    elif kind == 'end_expedition':
        if s['expedition']:
            s['expedition']['active'] = False
            s['expedition']['last'] = None
        s['location'] = None
    elif kind == 'location':
        if not fix or not body.expedition_id:
            fail('Brak pomiaru lub wyprawy.')
        record_location(s, fix, str(body.expedition_id), body.seq)
        if not s['points']:
            s['points'] = generate_world(fix)
    elif kind == 'search':
        if not fix:
            fail('Poczekaj na aktualną lokalizację GPS.')
        validate_fix(fix)
        if not s['expedition'] or not s['expedition']['active']:
            fail('Najpierw rozpocznij wyprawę.')
        # Remember cleared areas across rerolls so searching cannot reset a cooldown.
        now = time.time()
        areas = [p for p in s.get('cleared_areas', []) + s['points']
                 if p['type'] == 'spot' and p['cooldown_until'] > now]
        unique = {p['id']: p for p in areas}
        s['cleared_areas'] = list(unique.values())
        s['points'] = generate_world(fix)
        for point in s['points']:
            if point['type'] == 'spot':
                point['cooldown_until'] = max([p['cooldown_until'] for p in areas
                                              if distance(p, point) <= cfg.interaction_radius_m] or [0])
    elif kind == 'inspect':
        if point['type'] == 'spot':
            encounter(point)
    elif kind == 'battle_start':
        start_battle(s, point)
    elif kind == 'battle_action':
        battle_action(s, str(body.battle_id), body.turn, body.move)
    p.state = s
    # Never keep snapshots of coordinates in receipts. Location retries use the expedition sequence.
    result = {'ok': True}
    if kind != 'location':
        db.add(Receipt(player_id=p.id, key=str(body.key), fingerprint=fingerprint, response=result))
    db.commit()
    return result


@app.get('/api/health')
def health(db: DBSession = Depends(get_db)):
    db.execute(text('SELECT 1'))
    return {'status': 'ok'}


# Register SPA fallback last; never turn an unknown API endpoint into HTML.
DIST = Path(__file__).resolve().parents[2] / 'dist'
if DIST.is_dir():
    app.mount('/assets', StaticFiles(directory=DIST / 'assets'), name='assets')

    @app.get('/{path:path}')
    def frontend(path: str):
        if path.startswith('api/'):
            fail('Nie znaleziono endpointu.', 404)
        target = (DIST / path).resolve()
        if target.is_relative_to(DIST.resolve()) and target.is_file():
            return FileResponse(target)
        return FileResponse(DIST / 'index.html')
