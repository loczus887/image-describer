# Image Describer

System wspierający osoby niewidome i niedowidzące poprzez automatyczne generowanie opisów obrazów przy użyciu sztucznej inteligencji.

---

## Spis treści

1. [O projekcie](#o-projekcie)
2. [Architektura systemu](#architektura-systemu)
3. [Wymagania](#wymagania)
4. [Instalacja](#instalacja)
5. [Uruchomienie](#uruchomienie)
6. [Jak korzystać](#jak-korzystać)
7. [API Reference](#api-reference)
8. [Struktura projektu](#struktura-projektu)
9. [Konfiguracja](#konfiguracja)
10. [Rozwiązywanie problemów](#rozwiązywanie-problemów)

---

## O projekcie

### Cel

Image Describer umożliwia osobom z dysfunkcjami wzroku odbiór informacji wizualnych poprzez:

- Automatyczne rozpoznawanie zawartości obrazów
- Generowanie opisów w języku naturalnym (angielski)
- Odczyt głosowy opisu (Text-to-Speech)
- Zgodność z WCAG 2.1 AA

### Funkcje

| Funkcja | Opis |
|---------|------|
| Wczytywanie obrazu | Upload pliku lub wybór z menu kontekstowego |
| Przetwarzanie AI | Analiza obrazu modelem BLIP |
| Generowanie opisu | Opis w języku naturalnym |
| Odczyt głosowy | Web Speech API (TTS) |
| Historia opisów | Zapis i przeglądanie poprzednich wyników |
| Panel użytkownika | Ustawienia dostępności, high contrast |

### Tryby działania

1. **Aplikacja webowa** - upload obrazu z dysku
2. **Rozszerzenie Chrome** - prawy klik na obraz -> "Describe Image"

---

## Architektura systemu

```
+------------------------------------------------------------------+
|                    WARSTWA PREZENTACJI                           |
+--------------------------------+---------------------------------+
|   Aplikacja React (Web)        |   Rozszerzenie Chrome           |
|   - ImageUploader              |   - Context Menu                |
|   - DescriptionViewer          |   - Popup z wynikiem            |
|   - AudioPlayer (TTS)          |   - Background Script           |
|   - HistoryPanel               |                                 |
|   - SettingsPanel              |                                 |
+--------------------------------+---------------------------------+
                              |
                              v HTTP/REST API
+------------------------------------------------------------------+
|                    WARSTWA LOGIKI (Backend)                      |
|                         Python + FastAPI                         |
+------------------------------------------------------------------+
|  Endpointy:                                                      |
|  - POST /describe      -> generowanie opisu                      |
|  - GET/DELETE /history -> historia użytkownika                   |
|  - POST /login         -> uwierzytelnianie JWT                   |
|  - POST /register      -> rejestracja                            |
|  - GET /metrics        -> metryki systemu                        |
|  - /admin/*            -> panel administracyjny                  |
+------------------------------------------------------------------+
|  Serwisy:                                                        |
|  - DescriptionService  -> przetwarzanie obrazów                  |
|  - AIModelIntegration  -> komunikacja z BLIP                     |
|  - AuthService         -> JWT, hasła                             |
|  - MonitoringService   -> metryki, logi                          |
|  - ValidationService   -> walidacja plików (max 5MB)             |
+------------------------------------------------------------------+
                              |
                              v
+------------------------------------------------------------------+
|                    WARSTWA DANYCH                                |
+--------------------------------+---------------------------------+
|   SQLite Database              |   BLIP AI Model                 |
|   - users                      |   - Salesforce/blip-image-      |
|   - descriptions               |     captioning-base             |
|   - bug_reports                |   - Hugging Face Transformers   |
|   - metrics                    |                                 |
+--------------------------------+---------------------------------+
```

---

## Wymagania

### Backend

- Python 3.10+ (testowane na 3.14)
- pip (menedżer pakietów)
- ~2GB RAM dla modelu AI
- ~1GB miejsca na dysku (model + cache)

### Frontend

- Node.js 18+
- npm lub yarn

### Rozszerzenie Chrome

- Google Chrome 88+
- Tryb deweloperski włączony

---

## Instalacja

### 1. Klonowanie repozytorium

```bash
git clone <repository-url>
cd io
```

### 2. Backend (Python)

```bash
# Utwórz wirtualne środowisko
python -m venv venv

# Aktywuj środowisko
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Zainstaluj zależności
pip install -r requirements.txt
```

**Główne zależności:**

- `fastapi` - framework webowy
- `uvicorn` - serwer ASGI
- `transformers` - Hugging Face (AI)
- `torch` - PyTorch (deep learning)
- `sqlalchemy` - ORM bazy danych
- `python-jose` - JWT tokens
- `passlib` - hashowanie haseł

### 3. Frontend (React)

```bash
# Zainstaluj zależności
npm install
```

**Główne zależności:**

- `react` 18.2.0
- `react-router-dom` - routing
- `vite` - bundler

### 4. Rozszerzenie Chrome

1. Otwórz Chrome -> `chrome://extensions/`
2. Włącz "Tryb dewelopera" (prawy górny róg)
3. Kliknij "Załaduj rozpakowane"
4. Wybierz folder `extension/`

---

## Uruchomienie

### Szybki start (3 kroki)

```bash
# Terminal 1 - Backend
python -m uvicorn backend.api_controller:app --reload --port 8000

# Terminal 2 - Frontend
npm run dev

# Otwórz przeglądarkę
# http://localhost:5173
```

### Szczegółowe uruchomienie

#### Backend

```bash
# Aktywuj venv (jeśli nie aktywne)
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/macOS

# Uruchom serwer
python -m uvicorn backend.api_controller:app --reload --host 0.0.0.0 --port 8000

# Pierwsze uruchomienie pobierze model AI (~1GB)
# Może to zająć kilka minut
```

**Logi uruchomienia:**

```
INFO:     Uvicorn running on http://0.0.0.0:8000
[DB] Initializing database on first request...
[AI] Loading BLIP model... (pierwsze uruchomienie)
[AI] Model loaded successfully
```

#### Frontend

```bash
# Development mode
npm run dev

# Production build
npm run build
npm run preview
```

**Dostępne pod:** `http://localhost:5173`

#### Tworzenie konta administratora

```bash
python -m backend.create_admin_user
```

**Domyślne dane:**

- Login: `admin`
- Hasło: `admin123`
- Email: `admin@example.com`

---

## Jak korzystać

### Aplikacja webowa

#### 1. Rejestracja/Logowanie

1. Otwórz `http://localhost:5173`
2. Kliknij "Register" aby utworzyć konto
3. Wypełnij formularz (min. 8 znaków hasła)
4. Po rejestracji nastąpi automatyczne logowanie

#### 2. Opisywanie obrazu

1. **Drag & Drop** - przeciągnij obraz na stronę
2. **Kliknij** - wybierz plik z dysku
3. Poczekaj na przetworzenie (5-30 sekund)
4. Przeczytaj lub odsłuchaj opis

#### 3. Odczyt głosowy

- Kliknij przycisk **"Read Aloud"** pod opisem
- Użyj **Stop** aby zatrzymać
- Synteza mowy używa głosu systemowego

#### 4. Historia

- Panel **History** pokazuje poprzednie opisy
- Kliknij element aby wyświetlić opis
- **Clear History** - usuwa całą historię

#### 5. Ustawienia dostępności

Kliknij ikonę ustawień aby otworzyć panel:

- **High Contrast** - tryb wysokiego kontrastu
- **Font Size** - rozmiar czcionki (S/M/L)
- **Audio** - włącz/wyłącz TTS

### Rozszerzenie Chrome

#### 1. Logowanie

1. Kliknij ikonę rozszerzenia na pasku
2. Zaloguj się (te same dane co w aplikacji webowej)
3. Token zostanie zapamiętany

#### 2. Opisywanie obrazu na stronie

1. Kliknij prawym przyciskiem na dowolny obraz
2. Wybierz **"Describe Image"**
3. Opis pojawi się w popup

#### 3. Upload z popup

1. Kliknij ikonę rozszerzenia
2. Przeciągnij obraz lub kliknij "Choose file"
3. Poczekaj na opis

---

## API Reference

### Uwierzytelnianie

Wszystkie endpointy (oprócz `/health`, `/login`, `/register`) wymagają tokenu JWT:

```
Authorization: Bearer <token>
```

### Endpointy

#### POST /register

Rejestracja nowego użytkownika.

```json
// Request
{
  "username": "jan",
  "email": "jan@example.com",
  "password": "haslo123"
}

// Response 201
{
  "id": 1,
  "username": "jan",
  "email": "jan@example.com",
  "role": "user",
  "created_at": "2024-01-15T10:30:00"
}
```

#### POST /login

Logowanie i pobranie tokenu JWT.

```json
// Request
{
  "username": "jan",
  "password": "haslo123"
}

// Response 200
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

#### POST /describe

Generowanie opisu obrazu.

```bash
# Request (multipart/form-data)
curl -X POST http://localhost:8000/describe \
  -H "Authorization: Bearer <token>" \
  -F "file=@image.jpg"
```

```json
// Response 200
{
  "success": true,
  "description": "a cat sitting on a windowsill looking outside",
  "error": null
}
```

#### GET /history

Pobranie historii opisów użytkownika.

```bash
GET /history?limit=10
```

```json
// Response 200
[
  {
    "id": 1,
    "image_hash": "abc123...",
    "description": "a dog playing in the park",
    "created_at": "2024-01-15T10:30:00"
  }
]
```

#### DELETE /history

Usunięcie całej historii użytkownika.

```json
// Response 200
{
  "success": true,
  "deleted_count": 5,
  "message": "Deleted 5 history items"
}
```

#### GET /me

Informacje o zalogowanym użytkowniku.

```json
// Response 200
{
  "id": 1,
  "username": "jan",
  "email": "jan@example.com",
  "role": "user",
  "created_at": "2024-01-15T10:30:00"
}
```

#### GET /health

Sprawdzenie stanu serwera (bez autoryzacji).

```json
// Response 200
{
  "status": "healthy",
  "message": "Backend is running"
}
```

#### GET /metrics

Metryki systemu.

```json
// Response 200
{
  "uptime_seconds": 3600.5,
  "request_count": 150,
  "error_count": 3,
  "success_rate": 0.98
}
```

### Panel administracyjny

Wymaga roli `admin`:

| Endpoint | Metoda | Opis |
|----------|--------|------|
| `/admin/users` | GET | Lista użytkowników |
| `/admin/users/{id}` | PUT | Edycja użytkownika |
| `/admin/users/{id}` | DELETE | Usunięcie użytkownika |
| `/admin/metrics` | GET | Szczegółowe metryki |
| `/admin/reports` | GET | Zgłoszenia błędów |
| `/admin/reports/{id}` | PUT | Aktualizacja zgłoszenia |

---

## Struktura projektu

```
io/
|-- backend/                    # Serwer Python/FastAPI
|   |-- api_controller.py       # Główne endpointy REST API
|   |-- admin_controller.py     # Panel administracyjny
|   |-- create_admin_user.py    # Skrypt tworzenia admina
|   |
|   |-- auth/
|   |   +-- jwt_bearer.py       # Middleware JWT
|   |
|   |-- data/
|   |   |-- database.py         # Modele SQLAlchemy
|   |   +-- admin_repositories.py # Repozytoria danych
|   |
|   |-- models/
|   |   +-- auth_models.py      # Pydantic schemas
|   |
|   +-- services/
|       |-- ai_model_integration.py  # Integracja BLIP
|       |-- auth_service.py          # Logika uwierzytelniania
|       |-- description_service.py   # Przetwarzanie obrazów
|       |-- email_service.py         # Wysyłka email
|       |-- monitoring_service.py    # Metryki
|       +-- validation_service.py    # Walidacja plików
|
|-- src/                        # Frontend React
|   |-- main.jsx               # Entry point
|   |-- App.jsx                # Główny komponent
|   |-- App.css                # Style globalne
|   |
|   |-- components/
|   |   |-- ImageUploader.jsx   # Upload obrazów
|   |   |-- DescriptionViewer.jsx # Wyświetlanie opisu
|   |   |-- AudioPlayer.jsx     # Text-to-Speech
|   |   |-- HistoryPanel.jsx    # Historia opisów
|   |   |-- SettingsPanel.jsx   # Ustawienia dostępności
|   |   |-- Login.jsx           # Formularz logowania
|   |   +-- Register.jsx        # Formularz rejestracji
|   |
|   +-- contexts/
|       +-- AuthContext.jsx     # Kontekst uwierzytelniania
|
|-- extension/                  # Rozszerzenie Chrome
|   |-- manifest.json          # Konfiguracja rozszerzenia
|   |-- popup.html             # UI popup
|   |-- popup.js               # Logika popup
|   |-- popup.css              # Style popup
|   |-- background.js          # Service worker
|   +-- content.js             # Content script
|
|-- package.json               # Zależności npm
|-- requirements.txt           # Zależności Python
|-- vite.config.js            # Konfiguracja Vite
|-- .gitignore                # Ignorowane pliki
|
|-- README.md                  # Ten plik
|-- PRODUCTION_SETUP.md        # Wdrożenie produkcyjne
+-- REQUIREMENTS_CHECK.md      # Status wymagań
```

---

## Konfiguracja

### Zmienne środowiskowe

Utwórz plik `backend/.env`:

```bash
# JWT (WYMAGANE w produkcji)
JWT_SECRET_KEY=twoj-tajny-klucz-32-znaki-min
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# Email (opcjonalne)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=twoj-email@gmail.com
SMTP_PASSWORD=haslo-aplikacji
SMTP_FROM=noreply@twoja-domena.pl

# Baza danych (opcjonalne, domyślnie SQLite)
DATABASE_URL=sqlite:///./image_describer.db
```

### Limity

| Parametr | Wartość | Plik |
|----------|---------|------|
| Max rozmiar obrazu | 5 MB | `validation_service.py` |
| Token JWT wygasa | 30 min | `auth_service.py` |
| Historia limit | 10 elementów | `api_controller.py` |
| Timeout AI | 5 min | `App.jsx` |

### Obsługiwane formaty obrazów

- JPEG (.jpg, .jpeg)
- PNG (.png)
- WebP (.webp)
- GIF (.gif)

---

## Rozwiązywanie problemów

### Backend nie startuje

**Problem:** `ModuleNotFoundError: No module named 'xxx'`

```bash
# Rozwiązanie: Zainstaluj zależności
pip install -r requirements.txt
```

**Problem:** `Port 8000 already in use`

```bash
# Windows - znajdź i zabij proces
netstat -ano | findstr :8000
taskkill /PID <pid> /F

# Linux/macOS
lsof -i :8000
kill -9 <pid>
```

### Model AI nie ładuje się

**Problem:** `OutOfMemoryError` lub bardzo wolne ładowanie

```bash
# Rozwiązanie 1: Użyj CPU zamiast GPU
# W ai_model_integration.py ustaw device="cpu"

# Rozwiązanie 2: Zwiększ RAM (min. 2GB wolnego)
```

**Problem:** Pobieranie modelu trwa bardzo długo

Model BLIP ma ~1GB. Przy pierwszym uruchomieniu:

1. Poczekaj cierpliwie (5-15 minut zależnie od łącza)
2. Model zapisze się w cache (`~/.cache/huggingface/`)
3. Kolejne uruchomienia będą szybkie

### Frontend nie łączy się z backendem

**Problem:** `Network Error` lub `CORS`

1. Sprawdź czy backend działa: `curl http://localhost:8000/health`
2. Sprawdź konfigurację proxy w `vite.config.js`:

```javascript
export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  }
})
```

### Rozszerzenie Chrome nie działa

**Problem:** Context menu się nie pojawia

1. Otwórz `chrome://extensions/`
2. Kliknij "Odśwież" przy rozszerzeniu
3. Zamknij i otwórz ponownie przeglądarkę

**Problem:** "Invalid token" przy logowaniu

1. Sprawdź czy backend działa
2. Sprawdź URL w `extension/popup.js` (domyślnie `http://localhost:8000`)
3. Wyloguj się i zaloguj ponownie

### Błędy bazy danych

**Problem:** `no such column` lub `table doesn't exist`

```bash
# Rozwiązanie: Usuń starą bazę i uruchom ponownie
rm image_describer.db
python -m uvicorn backend.api_controller:app --reload
```

### Token wygasł

**Problem:** `401 Unauthorized` po pewnym czasie

Token JWT wygasa po 30 minutach. Rozwiązania:

1. Zaloguj się ponownie
2. Zwiększ `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` w `.env`

---

## Licencja

MIT License

---

## Kontakt

- GitHub Issues: [link do repozytorium]

---

*Dokumentacja projektu Image Describer v1.0*
