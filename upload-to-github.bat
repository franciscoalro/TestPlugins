@echo off
chcp 65001 >nul
echo.
echo ============================================
echo   UPLOAD PARA GITHUB - MAXSERIES PROJECT
echo ============================================
echo.

REM Configurar mensagem de commit
set COMMIT_MSG=Implementacao PlayerEmbedAPI ultra-rapida + Suite Kali

REM Adicionar todos os arquivos importantes
echo [+] Adicionando arquivos...
git add MaxSeriesProvider_Final.kt
git add PlayerEmbedAPIExtractor_Final.kt
git add PlayerEmbedAPIExtractor.kt
git add kali_*.py
git add hacker_*.py
git add ultra_fast_extractor.py
git add extract_minimal.py
git add playerembedapi_final_extractor.py
git add *.md
git add kali_analysis_*

echo.
echo [+] Criando commit...
git commit -m "%COMMIT_MSG%" -m "- Extracao PlayerEmbedAPI em ~250ms" -m "- Suite completa Kali Linux" -m "- Ferramentas: MITM Proxy, JS Deobfuscator, Param Fuzzer" -m "- Analise de seguranca completa" -m "- Documentacao tecnica"

echo.
echo [+] Enviando para GitHub...
git push origin main

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ============================================
    echo   ✅ UPLOAD CONCLUIDO COM SUCESSO!
    echo ============================================
    echo.
    echo Arquivos enviados:
    echo   - Implementacoes Kotlin
    echo   - Ferramentas Python
    echo   - Documentacao completa
    echo   - Relatorios de analise
    echo.
) else (
    echo.
    echo ============================================
    echo   ❌ ERRO NO UPLOAD
    echo ============================================
    echo.
)

pause
