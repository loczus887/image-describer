# 🚀 Quick Start Guide

## ✅ Status
System uwierzytelniania JWT został pomyślnie zaimplementowany i przetestowany!

## Szybki Start (3 kroki)

### 1. Uruchom Backend
```bash
# W terminalu 1
cd c:\Users\wikik\Downloads\io\io
python -m uvicorn backend.api_controller:app --host 0.0.0.0 --port 8000 --reload
```

Backend będzie dostępny na: `http://localhost:8000`

### 2. Utwórz Użytkownika Admin (już zrobione!)
```bash
# Admin już istnieje:
# Username: admin
# Password: admin123
# Email: admin@example.com
```

Jeśli chcesz utworzyć dodatkowych użytkowników:
```bash
python -m backend.create_admin_user username email@example.com password123
```

### 3. Uruchom Frontend
```bash
# W terminalu 2
npm run dev
```

Frontend będzie dostępny na: `http://localhost:5173`

## 🎯 Testowanie

### Przez przeglądarkę:
1. Otwórz `http://localhost:5173`
2. Zobaczysz ekran logowania
3. Zaloguj się jako **admin** / **admin123**
4. System Cię przekieruje do głównej aplikacji

### Przez API (curl):

**Rejestracja nowego użytkownika:**
```bash
curl -X POST http://localhost:8000/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@test.com","password":"testpass123"}'
```

**Logowanie:**
```bash
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

Otrzymasz:
```json
{
  "access_token": "eyJhbG...",
  "token_type": "bearer"
}
```

**Sprawdzenie użytkownika:**
```bash
curl http://localhost:8000/me \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

**Przesłanie obrazu:**
```bash
curl -X POST http://localhost:8000/describe \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -F "file=@image.jpg"
```

## ✨ Co działa

### ✅ Backend
- JWT Authentication (token ważny 30 minut)
- Endpointy: `/register`, `/login`, `/me`, `/logout`
- Zabezpieczone: `/describe`, `/history`, `/report-bug`
- Admin endpoints: `/admin/metrics`, `/admin/users`, `/admin/reports`
- Database: User, BugReport, Metric models
- Password hashing: pbkdf2_sha256

### ✅ Frontend
- AuthContext z zarządzaniem tokenami
- Login i Register forms
- Automatyczne wylogowanie przy wygasłym tokenie
- Zabezpieczone API calls
- Header z user info i logout button

## 🔧 Rozwiązywanie Problemów

### Backend nie startuje
```bash
# Sprawdź czy port 8000 jest wolny
netstat -ano | findstr :8000

# Jeśli zajęty, zabij proces lub użyj innego portu:
python -m uvicorn backend.api_controller:app --port 8001
```

### Frontend pokazuje 401 Unauthorized
- Sprawdź czy backend działa (`curl http://localhost:8000/health`)
- Sprawdź token w DevTools → Application → Local Storage
- Token wygasa po 30 minutach - zaloguj się ponownie

### Błąd: "no such column"
Stara baza danych! Usuń i utwórz nową:
```bash
rm image_describer.db
python -m backend.create_admin_user
```

### Bcrypt errors
Używamy pbkdf2_sha256 zamiast bcrypt (już naprawione w kodzie)

## 📚 API Documentation

Swagger UI: `http://localhost:8000/docs`
ReDoc: `http://localhost:8000/redoc`

## 🎉 Gotowe!

System jest w pełni funkcjonalny. Możesz:
- ✅ Rejestrować nowych użytkowników
- ✅ Logować się i otrzymywać JWT tokeny
- ✅ Używać wszystkich zabezpieczonych endpointów
- ✅ Zarządzać użytkownikami (jako admin)
- ✅ Zgłaszać błędy

**Wszyscy aktorzy z analizy są teraz obsługiwani!**

Pełna dokumentacja w [SETUP_GUIDE.md](./SETUP_GUIDE.md)
