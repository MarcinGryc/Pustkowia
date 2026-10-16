from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')
    database_url: str = 'postgresql+psycopg://pustkowia:pustkowia@localhost:5432/pustkowia'
    secret_key: str = 'local-development-change-this-secret-key'
    environment: str = 'development'
    app_origin: str = 'http://localhost:5173'
    demo_enabled: bool = False
    session_days: int = 14
    interaction_radius_m: int = 75
    max_accuracy_m: int = 50
    location_max_age_s: int = 45
    cooldown_seconds: int = 900
    defeat_cooldown_seconds: int = 180
    world_source: str = 'osm'
    overpass_url: str = 'https://overpass-api.de/api/interpreter'
    map_style_url: str = ''
    map_tiles_url: str = 'https://tile.openstreetmap.org/{z}/{x}/{y}.png'
    map_attribution: str = '© OpenStreetMap contributors'

    @property
    def production(self):
        return self.environment == 'production'


@lru_cache
def settings():
    s = Settings()
    if s.production and (len(s.secret_key) < 32 or s.secret_key.startswith('local-') or not s.app_origin.startswith('https://')):
        raise RuntimeError('Produkcja wymaga losowego SECRET_KEY (min. 32 znaki) i APP_ORIGIN z HTTPS.')
    if s.production and s.database_url.startswith('sqlite'):
        raise RuntimeError('Produkcja wymaga PostgreSQL.')
    if s.production and s.demo_enabled:
        raise RuntimeError('DEMO_ENABLED jest dostępny wyłącznie w środowisku developerskim.')
    return s
