@echo off
echo ========================================
echo    INICIANDO API DO ALIEXPRESS
echo ========================================
echo.

echo 🔧 Verificando Python...
python --version
if %errorlevel% neq 0 (
    echo ❌ Python não encontrado!
    pause
    exit /b 1
)

echo.
echo 🔧 Instalando dependências...
pip install flask flask-cors requests python-dotenv

echo.
echo 🚀 Iniciando API...
echo 📡 Endpoints:
echo    GET /api/search?keywords=smartphone
echo    GET /api/product/<id>
echo    GET /api/health
echo.
echo 🌐 API: http://localhost:3000
echo 📱 Rede: http://192.168.1.24:3000
echo.

cd /d "%~dp0"
python simple_api.py

pause 