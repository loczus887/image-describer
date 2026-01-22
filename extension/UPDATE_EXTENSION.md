# Aktualizacja Rozszerzenia Chrome z Autentykacją JWT

## 🔄 Co zostało zmienione

Rozszerzenie zostało zaktualizowane, aby działało z nowym systemem uwierzytelniania JWT.

### Nowe funkcje:
- ✅ Formularz logowania i rejestracji w popup
- ✅ Automatyczne sprawdzanie tokenu przy otwarciu
- ✅ Przechowywanie tokenu w `chrome.storage.local`
- ✅ Automatyczne wylogowanie przy wygasłym tokenie (401)
- ✅ Header z nazwą użytkownika i przyciskiem Logout

## 📝 Jak zaktualizować rozszerzenie

### Opcja 1: Zamień plik popup.js (Zalecane)

1. **Backup starego pliku:**
   ```bash
   cd c:\Users\wikik\Downloads\io\io\extension
   copy popup.js popup-OLD.js
   ```

2. **Zamień na nową wersję:**
   ```bash
   copy popup-with-auth.js popup.js
   ```

3. **Przeładuj rozszerzenie w Chrome:**
   - Otwórz `chrome://extensions`
   - Znajdź "Image Describer"
   - Kliknij przycisk "Reload" (🔄)

### Opcja 2: Ręczna aktualizacja

Edytuj `popup.js` i dodaj na początku:

```javascript
const TOKEN_KEY = 'auth_token';
const USER_KEY = 'user_data';
let currentToken = null;
let currentUser = null;
```

Następnie zaktualizuj funkcję `describeImage` aby dodawała header:

```javascript
const response = await fetch(`${API_URL}/describe`, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${currentToken}`  // DODAJ TO
  },
  body: formData,
});
```

## 🧪 Testowanie

1. **Otwórz rozszerzenie (kliknij ikonę w pasku Chrome)**

2. **Zobaczysz ekran logowania:**
   - Zaloguj się jako: `admin` / `admin123`
   - Lub zarejestruj nowe konto

3. **Po zalogowaniu:**
   - Zobaczysz nazwę użytkownika w headerze
   - Będzie przycisk "Logout"
   - Możesz normalnie używać rozszerzenia

4. **Testuj funkcje:**
   - Upload obrazu przez popup
   - Right-click na obrazie → "Describe Image"
   - Read Aloud

## 🔐 Jak działa autentykacja

1. **Pierwsze uruchomienie:**
   - Brak tokenu → pokazuje login screen
   - Logowanie → dostaje JWT token
   - Token zapisany w `chrome.storage.local`

2. **Kolejne uruchomienia:**
   - Sprawdza token w storage
   - Weryfikuje token przez `GET /me`
   - Jeśli ważny → pokazuje main interface
   - Jeśli nieważny → pokazuje login

3. **Podczas użycia:**
   - Każde żądanie `/describe` zawiera `Authorization: Bearer <token>`
   - Jeśli backend zwróci 401 → auto-logout

4. **Logout:**
   - Usuwa token z storage
   - Wraca do login screen

## 📁 Pliki

- `popup-with-auth.js` - Nowa wersja z autentykacją
- `popup.js` - Stara wersja (bez auth) - zastąp ją!
- `popup.css` - Zaktualizowane z style dla auth
- `popup.html` - Bez zmian
- `background.js` - Bez zmian
- `manifest.json` - Bez zmian

## ⚙️ Konfiguracja

Jeśli backend działa na innym porcie, zmień w `popup.js`:

```javascript
const API_URL = 'http://localhost:TWÓJ_PORT';
```

## 🐛 Rozwiązywanie Problemów

### "Connection error" przy logowaniu
- Sprawdź czy backend działa: `curl http://localhost:8000/health`
- Sprawdź URL w popup.js (powinno być `http://localhost:8000`)

### Token wygasa za szybko
- Token ważny 30 minut (konfigurowane w backend `.env`)
- Wyloguj się i zaloguj ponownie

### Rozszerzenie nie pokazuje login screen
- Wyczyść storage: DevTools → Application → Storage → Clear site data
- Przeładuj rozszerzenie

### Backend zwraca 401
- Token wygasł - kliknij Logout i zaloguj się ponownie
- Lub backend został zrestartowany (nowe hasła)

## ✅ Gotowe!

Po aktualizacji rozszerzenie będzie działać z systemem JWT authentication, tak samo jak aplikacja webowa! 🎉
