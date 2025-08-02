@echo off
echo 🌐 Configurando ngrok para acesso global...
echo.

REM Verificar se ngrok está instalado
where ngrok >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ ngrok não encontrado. Instalando...
    npm install -g ngrok
) else (
    echo ✅ ngrok já está instalado
)

echo.
echo 🚀 Iniciando túnel ngrok...
echo 📱 URL pública será exibida abaixo:
echo.

REM Iniciar ngrok
ngrok http 3000

pause 