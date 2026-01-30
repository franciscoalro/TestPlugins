@echo off
title Tester Bot MegaEmbed
cls
echo ==========================================
echo   INSTALANDO DEPENDENCIAS (PUPPETEER)...
echo ==========================================
call npm install
cls
echo ==========================================
echo   RODANDO TESTE...
echo ==========================================
node test.js
pause
