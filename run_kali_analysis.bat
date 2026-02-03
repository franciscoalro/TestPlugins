@echo off
chcp 65001 >nul
echo.
echo ================================================================================
echo                    KALI TOOLS - PlayerEmbedAPI Analysis
echo ================================================================================
echo.

if "%~1"=="" (
    echo Uso: run_kali_analysis.bat ^<URL^>
    echo.
    echo Exemplo:
    echo    run_kali_analysis.bat "https://playerembedapi.link/?v=kBJLtxCD3"
    echo.
    pause
    exit /b 1
)

set URL=%~1
echo [+] Analisando: %URL%
echo.

:: Executar analise master
echo [*] Fase 1: Analise Master...
python kali_master_analyzer.py --url "%URL%"

if errorlevel 1 (
    echo [!] Erro na analise master
    pause
    exit /b 1
)

:: Encontrar diretorio de analise
echo.
echo [*] Buscando resultados...
for /d %%D in (kali_analysis_*) do (
    set ANALYSIS_DIR=%%D
    goto :found_dir
)

echo [!] Diretorio de analise nao encontrado
pause
exit /b 1

:found_dir
echo [+] Diretorio de analise: %ANALYSIS_DIR%
echo.

:: Analisar JS se existir
if exist "%ANALYSIS_DIR%\core_bundle.js" (
    echo [*] Fase 2: Analise de JavaScript...
    python kali_js_deobfuscator.py --file "%ANALYSIS_DIR%\core_bundle.js" --output js_analysis.json
    echo.
)

:: Extrair sessao
echo [*] Fase 3: Extracao de Sessao...
python kali_session_extractor.py --url "%URL%" --save session_data.json
echo.

echo ================================================================================
echo                           ANALISE COMPLETA
echo ================================================================================
echo.
echo Resultados salvos em:
echo   - %ANALYSIS_DIR%/
echo   - js_analysis.json
echo   - session_data.json
echo.
echo Proximos passos:
echo   1. Analisar %ANALYSIS_DIR%\full_report.json
echo   2. Verificar js_analysis.json para strings de criptografia
echo   3. Usar kali_request_manipulator.py para testes manuais
echo.
pause
