@echo off
echo ========================================
echo    API FUNCIONAL DO ALIEXPRESS
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
echo 🔧 Verificando dependências...
pip install flask flask-cors requests python-dotenv

echo.
echo 🚀 Iniciando API funcional...
echo 📡 Endpoints disponíveis:
echo    GET /api/categories - Buscar categorias
echo    GET /api/search?category_id=2&keywords=smartphone - Buscar produtos
echo    GET /api/product/<id> - Detalhes do produto
echo    GET /api/health - Verificar saúde da API
echo.
echo 🌐 API rodando em: http://localhost:3000
echo 📱 Acessível em: http://192.168.1.24:3000
echo.
echo ⏹️  Pressione Ctrl+C para parar
echo.

python aliexpress_working_api.py

pause 