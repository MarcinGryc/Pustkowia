# Pustkowia

Mobilna gra RPG w przeglądarce: rzeczywista mapa okolicy, indywidualny świat gracza, osada, handel i walka turowa. Interfejs po polsku. Działa bez instalowania PWA. Projekt przygotowano do wdrożenia; nie opublikowano go na żadnym koncie.

## Wymagania

- Node.js 24 i npm, Python 3.13+.
- PostgreSQL 17, najprościej z Docker Compose.
- GPS wymaga bezpiecznego kontekstu: HTTPS lub `localhost`. Zwykłe HTTP pod adresem IP komputera nie wystarczy na telefonie.

## Uruchomienie lokalne

Z katalogu głównego, PowerShell:

```powershell
Copy-Item .env.example .env
docker compose up -d db
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r backend/requirements-dev.txt
$env:PYTHONPATH = 'backend'
.venv/Scripts/python.exe -m alembic upgrade head
.venv/Scripts/python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000 --no-access-log
```

W drugim terminalu:

```powershell
npm ci
npm run dev
```

Otwórz **http://localhost:5173**. Vite przekazuje `/api` do FastAPI, więc cookies i CSRF działają w tym samym originie. W `.env` pozostaw `APP_ORIGIN=http://localhost:5173`. Nie mieszaj `localhost` i `127.0.0.1` w adresie przeglądarki.

Linux/macOS: odpowiedniki poleceń Pythona to `.venv/bin/python`, a ustawienie ścieżki to `export PYTHONPATH=backend`.

### Wszystko w Dockerze

Po skopiowaniu `.env.example`:

```sh
docker compose --profile full up --build
```

Otwórz **http://localhost:8000**. Compose ustawia origin i wewnętrzny adres PostgreSQL. Migracje wykonuje start kontenera. Wolumen `postgres_data` zachowuje dane po restarcie. `docker compose down` nie usuwa wolumenu; nie używaj `down -v`, jeżeli chcesz zachować zapis.

### Jeden proces API i frontend, bez Dockera

```powershell
npm run build
$env:PYTHONPATH = 'backend'
$env:APP_ORIGIN = 'http://localhost:8000'
.venv/Scripts/python.exe -m alembic upgrade head
.venv/Scripts/python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --no-access-log
```

FastAPI obsługuje `dist/`, API oraz fallback SPA. Uruchamiaj polecenia z katalogu głównego. Po przebudowie frontendu uruchom backend ponownie, jeżeli wcześniej nie istniał katalog `dist`.

### Tryb demonstracyjny bez chodzenia

W lokalnym `.env` ustaw `ENVIRONMENT=development`, `DEMO_ENABLED=true`; opcjonalnie `WORLD_SOURCE=demonstration`, aby nie czekać na Overpass. Uruchom backend ponownie. Zarejestruj dowolne konto testowe, wybierz Start, a pod mapą włącz **DEMO**. Możesz:

- kliknąć mapę, aby przesunąć pozycję;
- wpisać współrzędne;
- otworzyć marker i wybrać „DEMO: ustaw pozycję tutaj”.

Pozycja odświeża się co 10 sekund. Zmiana punktu nie udaje przebytej drogi: filtr prędkości odrzuca nagłe przeskoki. Dane konta demonstracyjnego są rzeczywiste i trwałe, dlatego używaj oddzielnego konta do testów. Serwer odrzuci pozycję oznaczoną jako demo, gdy opcja jest wyłączona. Konfiguracja produkcyjna z `DEMO_ENABLED=true` nie uruchomi aplikacji.

Do samych testów backendu można użyć SQLite (automatycznie). Do lokalnego podglądu bez PostgreSQL można wyjątkowo ustawić `DATABASE_URL=sqlite:///test-results/preview.db` po utworzeniu `test-results/`. SQLite nie zapewnia blokad PostgreSQL i nie jest wariantem produkcyjnym.

## Konfiguracja środowiska

Wszystkie opcje czyta backend z `.env` lub środowiska. Konfiguracja mapy jest przekazywana przez `/api/bootstrap`, nie trzeba przebudowywać frontendu po jej zmianie.

| Zmienna | Domyślnie / znaczenie |
| --- | --- |
| `DATABASE_URL` | PostgreSQL, `postgresql+psycopg://user:password@host:5432/database`. Adresy `postgres://` i `postgresql://` z Rendera są automatycznie dostosowywane. |
| `SECRET_KEY` | Losowy sekret co najmniej 32 znaki w produkcji; służy do HMAC identyfikatorów sesji i limitów. Nie używaj wartości developerskiej. Zmiana wyloguje istniejące sesje. |
| `ENVIRONMENT` | `development` lokalnie, `production` na Renderze. Produkcja wymaga HTTPS, PostgreSQL i wyłączonego demo. |
| `APP_ORIGIN` | Dokładny publiczny origin bez końcowego `/`, np. `https://pustkowia.onrender.com`; lokalnie `http://localhost:5173`. Lista originów nie jest obsługiwana. |
| `DEMO_ENABLED` | `false`; `true` wyłącznie dla testów developerskich. |
| `SESSION_DAYS` | 14, bezwzględny czas życia sesji od logowania. |
| `INTERACTION_RADIUS_M` | 75 metrów. |
| `MAX_ACCURACY_M` | 50 metrów dla interakcji, do 35 metrów dla sumowania dystansu. |
| `LOCATION_MAX_AGE_S` | 45 sekund; dopuszczona różnica zegarów do 5 sekund w przyszłość. |
| `COOLDOWN_SECONDS` | 900 po zwycięstwie. |
| `DEFEAT_COOLDOWN_SECONDS` | 180 po porażce lub ucieczce. |
| `WORLD_SOURCE` | `osm`, opcjonalnie `demonstration`. |
| `OVERPASS_URL` | `https://overpass-api.de/api/interpreter`, zapytanie o geometrię ścieżek w okolicy. |
| `MAP_STYLE_URL` | Opcjonalny pełny URL stylu MapLibre; ma pierwszeństwo nad rastrem. |
| `MAP_TILES_URL` | Domyślnie `https://tile.openstreetmap.org/{z}/{x}/{y}.png`. |
| `MAP_ATTRIBUTION` | Widoczna atrybucja dostawcy rastra; domyślnie `© OpenStreetMap contributors`. Style wektorowe powinny mieć własną atrybucję źródeł. |
| `PORT` | Port usługi, domyślnie 8000 w Dockerze, dostarczany przez Render. |

Przykład wygenerowania sekretu:

```sh
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Katalog i balans: `backend/app/catalog.py`. Reguły walki i dystansu: `backend/app/game.py`. Zasięg i cooldowny: `.env`. PostGIS nie jest potrzebny dla siedmiu punktów gracza; serwer liczy odległość geodezyjną wzorem haversine.

### Mapa i dostępność miejsc

Domyślna mapa ulic i ścieżek używa kafli OSM i nie wymaga klucza. To publiczna usługa o ograniczonej pojemności, bez SLA. Przed szerszym uruchomieniem dobierz dostawcę do ruchu i jego warunków. Nie ma pobierania map offline ani prefetchingu kafli. Zasady: [OSM Tile Usage Policy](https://operations.osmfoundation.org/policies/tiles/), [MapLibre — źródło rastrowe](https://maplibre.org/maplibre-gl-js/docs/examples/map-tiles/).

Dostawcę wektorowego skonfiguruj np. przez `MAP_STYLE_URL=https://api.maptiler.com/maps/streets-v2/style.json?key=PUBLICZNY_KLUCZ` (po uzyskaniu własnego klucza i sprawdzeniu planu). Taki klucz trafia do przeglądarki: używaj tylko publicznego klucza ograniczonego do domeny, nigdy sekretu konta. Adresów z kluczami nie umieszczaj w repozytorium.

Przy pierwszej poprawnej lokalizacji backend próbuje znaleźć kandydatów na publicznych ścieżkach pieszych, drogach pieszych i drogach strefy zamieszkania w OSM, bez oznaczeń `private/no`. Miasto jest 200–500 m od startu; sześć spotów 100–1000 m. Brak siedmiu odpowiednich kandydatów lub awaria Overpass powoduje utworzenie **całego świata demonstracyjnego**, z ostrzeżeniem, że dostępność punktów nie została potwierdzona i nie należy kierować się do nich w terenie. Dane OSM również nie gwarantują aktualności, bezpieczeństwa ani legalnego dojścia. Świat zapisuje się i pozostaje stały przy odświeżaniu. Przycisk **SZUKAJ** nad mapą losuje nową osadę i sześć miejsc wokół aktualnej, świeżej pozycji GPS. Działa w trakcie wyprawy, poza walką. Odnowienie pobliskich miejsc po walce pozostaje zachowane również po ponownym losowaniu.

Przeglądarka wysyła kafle do dostawcy mapy, a backend przekazuje początkowe współrzędne do Overpass w celu wyszukania ścieżek. Serwer aplikacji nie zapisuje pełnych tras ani współrzędnych w logach dostępu (Docker wyłącza access log). Zapis zawiera bieżący pomiar, kotwicę dystansu, stałe punkty świata i sumy dzienne. Potwierdzenia operacji nie przechowują kopii pozycji.

## Render.com

1. Umieść projekt w swoim repozytorium Git. W Render wybierz **New → Blueprint** i wskaż repozytorium.
2. `render.yaml` tworzy jeden darmowy Web Service Docker oraz oddzielny płatny Render Postgres w tej samej lokalizacji. Sprawdź wycenę bazy, miejsca na dane i ewentualnego przekroczenia limitów przed utworzeniem zasobów. Nic nie zostało automatycznie wdrożone. Darmowy Web Service usypia się po 15 minutach bez ruchu; ponowne uruchomienie zajmuje około minuty. Limit darmowych godzin jest wspólny dla workspace. Szczegóły: [Render Free](https://render.com/docs/free).
3. Wymagany `APP_ORIGIN` ustaw na dokładny adres HTTPS usługi, np. `https://pustkowia.onrender.com`. Jeżeli Render przydzieli inną nazwę, popraw wartość i zrestartuj usługę. Przy własnej domenie ustaw jej origin.
4. `DATABASE_URL` jest pobierany z wewnętrznego adresu Render Postgres; `SECRET_KEY` generuje Render. Zostaw `ENVIRONMENT=production` i `DEMO_ENABLED=false`.
5. Docker buduje React i kopiuje wynik do obrazu Pythona. Start uruchamia `alembic upgrade head`, a następnie Uvicorn na `0.0.0.0:$PORT`. Kontrola zdrowia `/api/health` sprawdza połączenie z bazą.
6. Po wdrożeniu zarejestruj konto i sprawdź sesję oraz GPS przez HTTPS. Skonfiguruj kopie zapasowe bazy zgodnie z wybranym planem.

Jeżeli masz już bazę i Web Service, nie twórz kolejnego kompletu przez nowy Blueprint. W istniejącej usłudze wybierz plan Free i zachowaj połączenie z obecną bazą. Jeśli usługa jest zarządzana przez Blueprint, zsynchronizuj zmianę `plan: free` z repozytorium, żeby kolejna synchronizacja nie przywróciła płatnego planu. Przy ręcznym tworzeniu Web Service wybierz repozytorium, środowisko Docker, plan Free i region istniejącej bazy; ustaw `DATABASE_URL` na jej Internal Database URL, losowy `SECRET_KEY`, `ENVIRONMENT=production`, `DEMO_ENABLED=false` oraz `APP_ORIGIN` na publiczny adres HTTPS aplikacji bez końcowego `/`. Komendę startu zapewnia Dockerfile.

MVP zakłada **jedną instancję usługi** przy migracji wykonywanej w komendzie startu. Przed skalowaniem przenieś migrację do osobnego zadania/pre-deploy, żeby wiele instancji nie wykonywało jej jednocześnie. Same mutacje gry są serializowane w PostgreSQL blokadą wiersza gracza. Dokumentacja: [Render Blueprint](https://render.com/docs/blueprint-spec), [wdrożenia Docker](https://render.com/docs/docker).

## Testy

```powershell
npm run build
npm test
.venv/Scripts/python.exe -m pytest -q
```

Testy bez konfiguracji używają pliku SQLite w `test-results/`; dane są odtwarzane przed każdym testem. Testy PostgreSQL uruchamiaj tylko na **osobnej bazie testowej**, której nazwa kończy się `_test`, ponieważ zestaw usuwa i odtwarza tabele:

```powershell
docker compose exec db createdb -U pustkowia pustkowia_test
$env:TEST_DATABASE_URL = 'postgresql+psycopg://pustkowia:pustkowia@localhost:5432/pustkowia_test'
.venv/Scripts/python.exe -m pytest -q
```

Zestaw sprawdza rejestrację, normalizację e-maila, hasła Argon2, cookies, sesję po ponownym otwarciu klienta, wygasanie, wylogowanie, CSRF, limit logowań, izolację dwóch graczy, stały świat i spotkania, handel i ilości, brak złota, blokadę sprzedaży założonych przedmiotów, wyposażenie, zasięg/świeżość/dokładność, akcje i zapis walki, apteczki, ucieczkę, porażkę, zwycięstwo, awans, łupy, odnowienie oraz idempotencję. Są też testy filtrowania dryfu, skoków, przerw, duplikatów dystansu i dnia Europe/Warsaw. Cztery testy PostgreSQL sprawdzają równoległe zakupy z jednym kluczem, zakupy z różnymi kluczami bez przekroczenia salda, jednorazową nagrodę przy równoległych atakach oraz wydanie pojedynczego punktu rozwoju tylko raz. Dodatkowe testy obejmują nick, zgodność starszych zapisów, wyszukiwanie w nowej okolicy, regenerację online i offline oraz każdą premię za awans.

Workflow `.github/workflows/checks.yml` buduje frontend, uruchamia jego testy, wykonuje migracje i testuje backend z PostgreSQL 17. Przygotowanie workflow nie oznacza, że uruchomiono zdalne CI.

## Architektura, bezpieczeństwo i granice MVP

- React + TypeScript + Vite + Tailwind CSS, MapLibre GL JS. Proste własne ilustracje SVG. Manifest PWA; brak service workera, pamięci map offline i powiadomień.
- FastAPI + SQLAlchemy + Alembic. JSON w wierszu gracza to celowy agregat MVP: poziom, złoto, wyposażenie, grupowane przedmioty, świat, spotkania, walka i sumy dystansu zapisują się w jednej transakcji.
- Każda zmiana blokuje wiersz właściciela (`SELECT FOR UPDATE`). Unikalne `(player_id, key)` i odcisk treści zapewniają idempotencję zakupów, sprzedaży oraz akcji. Dodatkowo numer tury chroni walkę przed podwójną akcją, a numer pomiaru chroni dystans. Frontend blokuje powtórne kliknięcie i ponawia błąd transportu z tym samym kluczem. Nagrody przyznaje tylko zakończenie aktywnej walki.
- Losowe identyfikatory sesji są hashowane HMAC w bazie. Cookie sesji jest HttpOnly, SameSite=Lax, Secure i z prefiksem `__Host-` w produkcji. Token CSRF jest dostarczany przez bootstrap, wiązany z sesją i porównywany z nagłówkiem oraz cookie; dodatkowo każda operacja wymaga dokładnego `Origin`. Brak tokenów w localStorage i brak CORS.
- Limity logowania/rejestracji są atomowe i zapisane w bazie: 10 prób na e-mail i 60 na bezpośredni adres klienta w oknie 15 minut. Nagłówki przekazywane przez klienta nie są zaufane. Przy współdzielonym reverse proxy limit IP może grupować użytkowników; przed większą skalą zastosuj zaufaną konfigurację proxy i limit na brzegu sieci.
- Serwer sprawdza współrzędne, ich wiek, dokładność i odległość. To nie dowodzi fizycznej obecności: zegar i GPS klienta można podrobić. Nie ma pełnej ochrony antycheat.
- Dystans jest przybliżony, bez kroków i bez nagród. Widoczna strona przesyła pomiary nie częściej niż co 7 sekund, z dokładnością do 35 m dla sumy. Minimalny ruch to 10 m lub połowa sumy dokładności; prędkość do 3,5 m/s. Po przerwie ponad 45 s odcinek w linii prostej jest szacowany (maks. 3 km), z tym samym filtrem prędkości. Brak rekonstrukcji trasy i gwarancji działania przy blokadzie telefonu.
- Ekran Wake Lock jest opcjonalny i zależy od przeglądarki; po utracie widoczności przeglądarka może go zwolnić.
- Nowa postać zaczyna w koszulce i bokserkach, bez założonej broni ani pancerza. Nóż, kurtka i dwie apteczki są w plecaku. Każdy przedmiot ma własną ilustrację; założona broń i pancerz zmieniają warstwy SVG postaci w schronieniu, ekwipunku i walce. Nick podaje się przy rejestracji; starsze konta uzupełniają go po wejściu do gry.
- Awans przywraca HP i przyznaje jeden punkt do wyboru: +1 ataku, +1 obrony lub +5 maksymalnego HP (zwiększa też bieżące HP o 5). Punkty można zachować; kilka awansów daje kilka punktów. Progi to 100 × obecny poziom. Starsze zapisy zachowują dotychczasowe bonusy HP; wybór dotyczy kolejnych awansów.
- Poza walką odnawia się 1 HP na pełną minutę, do maksymalnego zdrowia, także po wylogowaniu. Serwer rozlicza czas przy kolejnym odczycie lub akcji, a otwarta gra odświeża zdrowie automatycznie. Apteczka daje natychmiastowe leczenie i rozpoczyna nową minutę regeneracji. Czas spędzony w walce nie nalicza regeneracji. Pistolet nie wymaga amunicji.
- Brak resetowania hasła, potwierdzania e-maila, administracji, automatycznego usuwania kont, zaawansowanej telemetrii i okresowego czyszczenia potwierdzeń operacji. Przed większym publicznym uruchomieniem zaplanuj te procesy i retencję danych. Zakres nie obejmuje questów, PvP, klanów, czatu, craftingu ani płatności.

### Weryfikacja w środowisku wykonania

Uruchomiono build frontendu, 5 testów frontendu, migracje Alembic i 36 testów backendu z przenośnym PostgreSQL 18.4, w tym wszystkie cztery testy współbieżności. Zestaw działa również lokalnie na SQLite; testy współbieżności są wtedy pomijane. Audyty npm i lokalnych zależności Pythona po aktualizacjach nie wykazały znanych podatności.

Testy API symulują współrzędne i odświeżenie klienta — nie są testem rzeczywistego GPS na telefonie. Narzędzie przeglądarkowe zgłosiło brak dostępnej przeglądarki, więc nie wykonano wizualnego testu telefonu. Warianty SVG postaci i ilustracje przedmiotów wyrenderowano do PNG i sprawdzono wizualnie. Obraz Docker i Render wymagają osobnej weryfikacji w środowisku z Dockerem lub na docelowej usłudze. Build zgłasza ostrzeżenie o wielkości pakietu biblioteki mapy; mapa jest ładowana dopiero przy otwieraniu wyprawy.
