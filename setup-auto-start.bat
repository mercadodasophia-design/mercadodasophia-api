@echo off
echo 🚀 Configurando inicialização automática da API...
echo.

REM Obter o caminho atual
set "CURRENT_DIR=%~dp0"
set "SCRIPT_PATH=%CURRENT_DIR%start-api.bat"

echo 📍 Caminho do script: %SCRIPT_PATH%
echo.

REM Criar tarefa agendada para iniciar com o Windows
schtasks /create /tn "MercadoDaSophia-API" /tr "%SCRIPT_PATH%" /sc onstart /ru "%USERNAME%" /f

if %errorlevel% equ 0 (
    echo ✅ Tarefa agendada criada com sucesso!
    echo 📱 A API iniciará automaticamente quando você ligar o PC
    echo.
    echo 🔧 Para remover a inicialização automática:
    echo    schtasks /delete /tn "MercadoDaSophia-API" /f
) else (
    echo ❌ Erro ao criar tarefa agendada
    echo 💡 Execute como administrador se necessário
)

echo.
echo 🎯 Para testar agora:
echo    %SCRIPT_PATH%
echo.
pause 