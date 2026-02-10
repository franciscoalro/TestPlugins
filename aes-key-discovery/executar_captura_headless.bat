@echo off
echo ============================================================
echo  Captura Headless - PlayerEmbedAPI
echo ============================================================
echo.

REM Verificar se Node.js esta instalado
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] Node.js nao esta instalado!
    echo.
    echo Por favor, instale Node.js:
    echo https://nodejs.org/
    echo.
    pause
    exit /b 1
)

echo [OK] Node.js encontrado
echo.

REM Verificar se Puppeteer esta instalado
if not exist "node_modules\puppeteer" (
    echo [INFO] Puppeteer nao encontrado. Instalando...
    echo.
    call npm install puppeteer
    echo.
    if %ERRORLEVEL% NEQ 0 (
        echo [ERRO] Falha ao instalar Puppeteer
        pause
        exit /b 1
    )
    echo [OK] Puppeteer instalado com sucesso!
    echo.
)

echo ============================================================
echo  Iniciando captura...
echo ============================================================
echo.

REM Executar script
cd aes-key-discovery
node capture_headless.js

echo.
echo ============================================================
echo  Captura finalizada!
echo ============================================================
echo.

REM Verificar se arquivo foi criado
if exist "output\algorithm_captured.json" (
    echo [OK] Arquivo gerado: output\algorithm_captured.json
    echo.
    echo Deseja abrir o arquivo? (S/N)
    set /p OPEN=
    if /i "%OPEN%"=="S" (
        start notepad output\algorithm_captured.json
    )
) else (
    echo [AVISO] Arquivo nao foi gerado
    echo Verifique os logs acima para detalhes
)

echo.
pause
