# Project Structure

```
io/
├── backend/                    # Backend Layer
│   ├── __init__.py
│   ├── api_controller.py      # FastAPI routes (APIController)
│   ├── main.py                 # Entry point
│   ├── data/                   # Data Layer
│   │   ├── __init__.py
│   │   ├── database.py         # SQLAlchemy models & setup
│   │   ├── repositories.py     # UserRepository, PreferencesRepository, DescriptionRepository
│   │   └── cache_manager.py    # In-memory cache
│   └── services/               # Business Logic Layer
│       ├── __init__.py
│       ├── description_service.py    # Orchestrates processing flow
│       ├── ai_model_integration.py    # Local BLIP model (generateDescription)
│       ├── image_processor.py        # Image validation, preprocessing, resizing
│       ├── validation_service.py     # File validation
│       └── monitoring_service.py     # Metrics tracking
├── src/                        # Frontend Layer
│   ├── App.jsx                 # Main UI component (opiszObraz)
│   ├── App.css
│   ├── main.jsx
│   ├── index.css               # Global styles with High Contrast support
│   └── components/
│       ├── ImageUploader.jsx
│       ├── DescriptionViewer.jsx
│       ├── AudioPlayer.jsx     # Web Speech API
│       ├── HistoryPanel.jsx
│       └── SettingsPanel.jsx
├── extension/                  # Browser Extension (Manifest V3)
│   ├── manifest.json
│   ├── popup.html
│   ├── popup.js
│   ├── popup.css
│   ├── background.js           # Service worker
│   ├── content.js              # Content script
│   └── icons/                  # Extension icons
├── requirements.txt            # Python dependencies
├── package.json                # Node dependencies
├── vite.config.js             # Vite configuration
├── run_backend.py             # Backend startup script
└── README.md
```

## Key Method Names (Per Requirements)

- `executeQuery` - Repository methods (UserRepository, PreferencesRepository, DescriptionRepository)
- `handleDescribeRequest` - API endpoint in api_controller.py
- `generateDescription` - AIModelIntegration method
- `opiszObraz` - Frontend trigger function in App.jsx

## Data Flow

1. User uploads image via `ImageUploader`
2. `opiszObraz()` called in `App.jsx`
3. Request sent to `POST /describe` endpoint
4. `handleDescribeRequest()` in `APIController` receives request
5. `DescriptionService.processImage()` orchestrates:
   - `ValidationService` validates file
   - `ImageProcessor` validates, preprocesses, resizes
   - `CacheManager` checks cache
   - `AIModelIntegration.generateDescription()` generates caption
   - `DescriptionRepository` saves to database
6. Response returned to frontend
7. `DescriptionViewer` displays text
8. `AudioPlayer` reads aloud (if enabled)

