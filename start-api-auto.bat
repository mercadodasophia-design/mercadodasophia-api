@echo off
title Mercado da Sophia - API Server
color 0A

echo.
echo 🚀 Mercado da Sophia - API Server
echo =================================
echo.

REM Verificar se Node.js está instalado
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Node.js não encontrado!
    echo 💡 Instale o Node.js primeiro
    pause
    exit /b 1
)

REM Verificar se as dependências estão instaladas
if not exist "node_modules" (
    echo 📦 Instalando dependências...
    npm install
    if %errorlevel% neq 0 (
        echo ❌ Erro ao instalar dependências
        pause
        exit /b 1
    )
)

echo ✅ Dependências verificadas
echo.

REM Obter IP da máquina
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr "IPv4"') do (
    set "IP=%%a"
    goto :found_ip
)
:found_ip
set "IP=%IP: =%"

echo 🌐 IP da máquina: %IP%
echo 📱 URL da API: http://%IP%:3000
echo.

echo 🚀 Iniciando servidor...
echo ⏹️  Pressione Ctrl+C para parar
echo.

REM Iniciar o servidor
npm start

echo.
echo ⏹️  Servidor parado
pause 