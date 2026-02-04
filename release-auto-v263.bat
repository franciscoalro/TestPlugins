@echo off
chcp 65001 >nul
echo ==========================================
echo   MaxSeries Release Automatizado v263
echo ==========================================
echo.

:: Verificar GITHUB_TOKEN
if "%GITHUB_TOKEN%"=="" (
    echo ❌ GITHUB_TOKEN nao definido!
    echo Defina com: set GITHUB_TOKEN=seu_token
    exit /b 1
)

echo ✅ GITHUB_TOKEN definido

:: Compilar
echo.
echo ==========================================
echo   1. Compilando Projeto
echo ==========================================
cd MaxSeries
call ..\gradlew.bat clean assembleRelease -x test --no-daemon
if %errorlevel% neq 0 (
    echo ❌ Falha na compilacao!
    cd ..
    exit /b 1
)
echo ✅ Build concluido!
cd ..

:: Copiar arquivo
echo.
echo ==========================================
echo   2. Gerando .cs3
echo ==========================================
copy /Y "MaxSeries\build\outputs\aar\MaxSeries-release.aar" "MaxSeries.cs3"
echo ✅ MaxSeries.cs3 gerado

:: Calcular hash
echo.
echo ==========================================
echo   3. Calculando Hash
echo ==========================================
for /f "tokens=*" %%a in ('certutil -hashfile MaxSeries.cs3 SHA256 ^| findstr /v "SHA256" ^| findstr /v "CertUtil"') do (
    set FILE_HASH=%%a
    set FILE_HASH=!FILE_HASH: =!
)
echo SHA256: %FILE_HASH%

:: Obter tamanho
for %%F in (MaxSeries.cs3) do set FILE_SIZE=%%~zF
echo Tamanho: %FILE_SIZE% bytes

:: Commit e Push
echo.
echo ==========================================
echo   4. Commit e Push
echo ==========================================
git add .
git commit -m "Release v263 - PlayerEmbedAPI Otimizado (V8 prioritario + V7 timeout 25s)"
git push origin main
echo ✅ Codigo enviado!

:: Criar release usando Python (mais confiavel)
echo.
echo ==========================================
echo   5. Criando Release no GitHub
echo ==========================================
python create-release-v263.py
if %errorlevel% neq 0 (
    echo ❌ Falha ao criar release
    exit /b 1
)

echo.
echo ==========================================
echo   Release v263 Concluido! 🎉
echo ==========================================
pause
