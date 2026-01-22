@echo off
REM Start script for Image Describer (Windows)

echo Starting Image Describer...

REM Start backend
echo Starting backend server...
start "Backend" cmd /k "python run_backend.py"

REM Wait a bit
timeout /t 3 /nobreak >nul

REM Start frontend
echo Starting frontend server...
start "Frontend" cmd /k "npm run dev"

echo.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo.
echo Press any key to exit...
pause >nul

