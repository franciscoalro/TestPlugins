@echo off
REM Script para executar análise via WSL no Windows

echo ========================================
echo   AES Key Discovery - WSL Launcher
echo ========================================
echo.

REM Verificar se WSL está instalado
wsl --status >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] WSL nao esta instalado!
    echo.
    echo Instale o WSL com:
    echo   wsl --install
    echo.
    pause
    exit /b 1
)

echo [OK] WSL detectado
echo.

REM Obter caminho atual
set "CURRENT_DIR=%CD%"
echo Diretorio atual: %CURRENT_DIR%
echo.

REM Converter caminho do Windows para WSL
REM C:\Users\... -> /mnt/c/Users/...
set "WSL_PATH=%CURRENT_DIR:\=/%"
set "WSL_PATH=%WSL_PATH:C:=/mnt/c%"
set "WSL_PATH=%WSL_PATH:D:=/mnt/d%"
set "WSL_PATH=%WSL_PATH:E:=/mnt/e%"

echo Caminho WSL: %WSL_PATH%
echo.

echo ========================================
echo   Escolha uma opcao:
echo ========================================
echo.
echo 0. Instalar Dependencias
echo 1. Teste Rapido (quick_test.sh)
echo 2. Analise Completa (run_analysis.sh)
echo 3. Burp Suite - Instrucoes
echo 4. mitmproxy - Captura
echo 5. Wireshark - Instrucoes
echo 6. Abrir WSL no diretorio
echo.
set /p choice="Digite o numero da opcao: "

if "%choice%"=="0" (
    echo.
    echo Instalando dependencias...
    wsl cd "%WSL_PATH%" ^&^& chmod +x install_dependencies.sh ^&^& bash install_dependencies.sh
    goto end
)

if "%choice%"=="1" (
    echo.
    echo Executando teste rapido...
    wsl cd "%WSL_PATH%" ^&^& chmod +x quick_test.sh ^&^& bash quick_test.sh
    goto end
)

if "%choice%"=="2" (
    echo.
    echo Executando analise completa...
    wsl cd "%WSL_PATH%" ^&^& chmod +x run_analysis.sh ^&^& chmod +x scripts/*.sh ^&^& bash run_analysis.sh
    goto end
)

if "%choice%"=="3" (
    echo.
    echo Abrindo instrucoes do Burp Suite...
    wsl cd "%WSL_PATH%" ^&^& chmod +x scripts/burp_intercept.sh ^&^& bash scripts/burp_intercept.sh
    goto end
)

if "%choice%"=="4" (
    echo.
    echo Iniciando mitmproxy...
    echo Configure seu navegador para usar proxy 127.0.0.1:8080
    echo.
    wsl cd "%WSL_PATH%" ^&^& mitmproxy -p 8080 -s scripts/mitmproxy_capture.py
    goto end
)

if "%choice%"=="5" (
    echo.
    echo Abrindo instrucoes do Wireshark...
    wsl cd "%WSL_PATH%" ^&^& chmod +x scripts/wireshark_filter.sh ^&^& bash scripts/wireshark_filter.sh
    goto end
)

if "%choice%"=="6" (
    echo.
    echo Abrindo WSL...
    wsl cd "%WSL_PATH%" ^&^& bash
    goto end
)

echo.
echo [ERRO] Opcao invalida!
echo.

:end
echo.
echo ========================================
pause
