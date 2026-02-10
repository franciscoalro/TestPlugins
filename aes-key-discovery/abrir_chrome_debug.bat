@echo off
echo ============================================================
echo  Abrindo Chrome sem protecao anti-debug
echo ============================================================
echo.

REM Fechar todos os Chrome abertos
taskkill /F /IM chrome.exe 2>nul
timeout /t 2 /nobreak >nul

REM Criar pasta temporaria
if not exist "C:\temp\chrome_debug" mkdir "C:\temp\chrome_debug"

echo Abrindo Chrome...
echo.
echo INSTRUCOES:
echo 1. Pressione F12 para abrir DevTools
echo 2. Va para a aba Console
echo 3. Abra o arquivo: CAPTURAR_SEM_DEBUGGER.md
echo 4. Copie e cole o codigo JavaScript
echo 5. Acesse: https://playerembedapi.link/?v=kBJLtxCD3
echo.

REM Abrir Chrome com flags anti-debug
start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" --disable-blink-features=AutomationControlled --disable-web-security --user-data-dir="C:\temp\chrome_debug" about:blank

echo.
echo Chrome aberto! Siga as instrucoes acima.
echo.
pause
