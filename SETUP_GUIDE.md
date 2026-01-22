# Image Describer - Setup Guide with Authentication

## ✅ Co zostało zaimplementowane

### Backend (Python/FastAPI)
- ✅ System uwierzytelniania JWT
- ✅ Endpointy: `/register`, `/login`, `/me`, `/logout`
- ✅ Zabezpieczone endpointy `/describe` i `/history`
- ✅ Panel administracyjny (`/admin/*`)
- ✅ System raportowania błędów (`/report-bug`)
- ✅ Rozszerzone monitorowanie (metryki z response times)
- ✅ Modele BugReport i Metric w bazie danych
- ✅ Role użytkowników (user/admin)
- ✅ Email service (podstawowy SMTP)

### Frontend (React)
- ✅ AuthContext z zarządzaniem tokenami JWT
- ✅ Komponenty Login i Register
- ✅ Zabezpieczone API calls przez authenticatedFetch
- ✅ Header z informacją o użytkowniku i przyciskiem Logout
- ✅ Automatyczne wylogowanie przy wygasłym tokenie

## 🚀 Szybki Start

### 1. Uruchomienie Backendu

```bash
# Przejdź do katalogu projektu
cd c:\Users\wikik\Downloads\io\io

# Backend jest już skonfigurowany z .env file
# JWT_SECRET_KEY jest już wygenerowany

# Uruchom backend
python run_backend.py
```

Backend będzie działał na `http://localhost:8000`

### 2. Utworzenie Użytkownika Admin

```bash
cd backend
python create_admin_user.py

# Domyślne dane logowania:
# Username: admin
# Password: admin123
# Email: admin@example.com
```

Możesz też podać własne dane:
```bash
python create_admin_user.py myusername myemail@example.com mypassword
```

### 3. Uruchomienie Frontendu

```bash
# W nowym terminalu
npm run dev
```

Frontend będzie działał na `http://localhost:5173`

### 4. Testowanie

1. Otwórz przeglądarkę na `http://localhost:5173`
2. Zobaczysz ekran logowania
3. Zarejestruj nowego użytkownika lub zaloguj się jako admin
4. Po zalogowaniu zobaczysz główną aplikację z przyciskiem "Logout"

## 📝 API Endpoints

### Publiczne
- `POST /register` - Rejestracja (username, email, password)
- `POST /login` - Logowanie (username, password) → zwraca JWT token
- `GET /health` - Health check

### Wymagające Autentykacji (Bearer Token)
- `GET /me` - Informacje o zalogowanym użytkowniku
- `POST /describe` - Opis obrazu (wymaga pliku)
- `GET /history` - Historia opisów użytkownika
- `POST /report-bug` - Zgłoszenie błędu
- `POST /logout` - Wylogowanie

### Admin Panel (wymaga role="admin")
- `GET /admin/metrics?hours=24` - Metryki systemu
- `GET /admin/users` - Lista użytkowników
- `PUT /admin/users/{id}` - Aktualizacja użytkownika
- `DELETE /admin/users/{id}` - Usunięcie użytkownika
- `GET /admin/reports` - Lista raportów błędów
- `PUT /admin/reports/{id}` - Aktualizacja raportu

## 🔐 Autentykacja

### Jak działa JWT

1. Użytkownik loguje się przez `/login`
2. Otrzymuje JWT token (ważny 30 minut)
3. Token zapisywany w `localStorage`
4. Każde żądanie zawiera header: `Authorization: Bearer <token>`
5. Backend weryfikuje token przed przetworzeniem żądania

### Przykład użycia w JavaScript

```javascript
// Logowanie
const response = await fetch('/api/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ username: 'admin', password: 'admin123' })
})
const { access_token } = await response.json()

// Zabezpieczone żądanie
const result = await fetch('/api/describe', {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${access_token}` },
  body: formData
})
```

## 📊 Panel Administracyjny (TODO)

Panel admin nie jest jeszcze zaimplementowany w frontend, ale backend endpoints są gotowe.

### Dostępne funkcje przez API:
- Przeglądanie metryk systemu
- Zarządzanie użytkownikami (blokowanie, usuwanie)
- Przeglądanie raportów błędów
- Zmiana statusu raportów

### Implementacja frontend (do zrobienia):
- Routing do `/admin`
- Komponenty: AdminDashboard, AdminUsers, AdminReports
- Wykresy (Chart.js)

## 🧪 Testowanie API z curl

### Rejestracja
```bash
curl -X POST http://localhost:8000/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@test.com","password":"testpass123"}'
```

### Logowanie
```bash
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"testpass123"}'
```

### Sprawdzenie użytkownika (wymaga tokenu)
```bash
curl http://localhost:8000/me \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Opis obrazu (wymaga tokenu)
```bash
curl -X POST http://localhost:8000/describe \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -F "file=@image.jpg"
```

## 🔧 Konfiguracja

### Zmienne środowiskowe (.env)

Plik `backend/.env` zawiera:
```env
JWT_SECRET_KEY=<bezpieczny-klucz>
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM=noreply@imagedescriber.com
```

**Ważne:** Zmień `JWT_SECRET_KEY` na produkcji!

### SMTP Email (opcjonalne)

Aby włączyć wysyłanie emaili:
1. Skonfiguruj SMTP w `.env`
2. Dla Gmail: wygeneruj "App Password" w ustawieniach konta
3. Email będzie wysyłany po rejestracji

## 📁 Struktura Plików

```
io/
├── backend/
│   ├── auth/
│   │   ├── __init__.py
│   │   └── jwt_bearer.py          # JWT dependencies
│   ├── data/
│   │   ├── database.py             # Modele (User, BugReport, Metric)
│   │   ├── repositories.py         # CRUD operations
│   │   └── admin_repositories.py   # Admin queries
│   ├── models/
│   │   └── auth_models.py          # Pydantic models
│   ├── services/
│   │   ├── auth_service.py         # Autentykacja i JWT
│   │   ├── email_service.py        # SMTP email
│   │   └── monitoring_service.py   # Metryki (rozszerzone)
│   ├── api_controller.py           # Main API + auth endpoints
│   ├── admin_controller.py         # Admin endpoints
│   ├── migrate_add_auth.py         # Migration script
│   ├── create_admin_user.py        # Admin user creator
│   └── .env                        # Configuration
├── src/
│   ├── contexts/
│   │   └── AuthContext.jsx         # Auth state management
│   ├── components/
│   │   ├── Login.jsx               # Login form
│   │   ├── Register.jsx            # Register form
│   │   └── Login.css               # Auth styles
│   ├── App.jsx                     # Main app (z auth)
│   └── main.jsx                    # React entry (z BrowserRouter)
├── package.json                    # + react-router-dom, chart.js
└── requirements.txt                # + passlib, python-jose, dotenv
```

## 🐛 Rozwiązywanie Problemów

### Backend nie startuje
```bash
# Sprawdź czy wszystkie dependencies są zainstalowane
pip list | grep -E "(fastapi|passlib|jose)"

# Reinstall dependencies
pip install -r requirements.txt
```

### Frontend pokazuje błąd 401
- Sprawdź czy backend działa na porcie 8000
- Sprawdź czy token jest w localStorage (DevTools → Application → Local Storage)
- Sprawdź czy token nie wygasł (30 min)

### Nie można się zalogować
- Sprawdź czy użytkownik istnieje w bazie
- Sprawdź hasło (min. 8 znaków)
- Zobacz logi backend w terminalu

### CORS errors
CORS middleware jest wyłączony. Jeśli potrzebujesz, włącz w `api_controller.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## ✨ Następne Kroki

1. **Panel Admin w Frontend**
   - Implementuj routing do `/admin`
   - Dodaj komponenty AdminDashboard, AdminUsers, AdminReports
   - Użyj Chart.js do wizualizacji metryk

2. **Rozszerzenia**
   - Password reset flow
   - Email verification
   - Refresh tokens
   - Rate limiting
   - CSRF protection

3. **Testy**
   - Unit testy (pytest dla backend, Jest dla frontend)
   - Integration testy dla API
   - E2E testy z Playwright

## 📚 Dokumentacja

- FastAPI Docs: `http://localhost:8000/docs` (Swagger UI)
- Redoc: `http://localhost:8000/redoc`
- Model diagramy dostępne w `/backend/data/database.py`

## 🎉 Gotowe!

System autentykacji jest w pełni funkcjonalny. Możesz teraz:
- ✅ Rejestrować użytkowników
- ✅ Logować się i otrzymywać JWT tokeny
- ✅ Używać zabezpieczonych endpointów
- ✅ Zarządzać użytkownikami przez admin API
- ✅ Zgłaszać błędy przez `/report-bug`

Wszyscy zdefiniowani aktorzy są teraz obsługiwani przez system!
