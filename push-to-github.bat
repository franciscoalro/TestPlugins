@echo off
echo ========================================
echo   PUSH PARA GITHUB - TESTPLUGINS
echo ========================================
echo.
echo Executando: git push -u origin main
echo.
echo Quando solicitado:
echo   Username: franciscoalro
echo   Password: [sua senha]
echo.
echo ========================================
echo.

cd /d "d:\TestPlugins-master"
git push -u origin main

echo.
echo ========================================
echo   PUSH CONCLUIDO!
echo ========================================
echo.
echo Acesse: https://github.com/franciscoalro/TestPlugins/actions
echo Para acompanhar o build
echo.
pause
