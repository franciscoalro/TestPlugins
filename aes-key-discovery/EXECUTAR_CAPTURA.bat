@echo off
REM Script para executar captura automatizada via WSL

echo.
echo ========================================================================
echo   CAPTURA AUTOMATIZADA - Algoritmo de Decriptacao
echo ========================================================================
echo.

REM Verificar se WSL esta instalado
wsl --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] WSL nao encontrado!
    echo.
    echo Por favor, instale o WSL primeiro:
    echo   1. Abra PowerShell como Administrador
    echo   2. Execute: wsl --install
    echo   3. Reinicie o computador
    echo   4. Execute este script novamente
    echo.
    pause
    exit /b 1
)

echo [OK] WSL encontrado
echo.

REM Converter caminho do Windows para WSL
set "CURRENT_DIR=%~dp0"
set "WSL_PATH=%CURRENT_DIR:\=/%"
set "WSL_PATH=%WSL_PATH:C:=/mnt/c%"
set "WSL_PATH=%WSL_PATH:D:=/mnt/d%"
set "WSL_PATH=%WSL_PATH:E:=/mnt/e%"

echo Diretorio: %CURRENT_DIR%
echo.

echo ========================================================================
echo   Executando captura no WSL...
echo ========================================================================
echo.

REM Executar script no WSL
wsl bash -c "cd '%WSL_PATH%' && chmod +x run_capture_wsl.sh && ./run_capture_wsl.sh"

set EXIT_CODE=%errorlevel%

echo.
echo ========================================================================

if %EXIT_CODE% equ 0 (
    echo.
    echo   [SUCESSO] Captura concluida!
    echo.
    echo   Resultados salvos em:
    echo     %CURRENT_DIR%output\algorithm_captured.json
    echo.
    echo   Para visualizar:
    echo     notepad %CURRENT_DIR%output\algorithm_captured.json
    echo.
) else (
    echo.
    echo   [FALHA] Captura nao foi bem-sucedida
    echo.
    echo   Tente:
    echo     1. Executar novamente este script
    echo     2. Verificar logs acima
    echo     3. Usar metodo manual: SOLUCAO_FINAL.md
    echo.
)

echo ========================================================================
echo.

pause
exit /b %EXIT_CODE%
