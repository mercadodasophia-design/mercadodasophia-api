@echo off
echo 🚀 Starting Mercado da Sophia API Server...
echo.

cd /d "%~dp0"

echo 📦 Installing dependencies...
npm install

echo.
echo 🔥 Starting server...
npm start

pause 