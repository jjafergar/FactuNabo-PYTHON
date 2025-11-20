@echo off
REM Script de compilación rápida para FactuNabo
REM Para compilación completa con verificaciones, usa build_all.bat

echo Compilando FactuNabo...
echo.

REM Limpia artefactos anteriores
if exist build rd /s /q build
if exist dist rd /s /q dist

echo Ejecutando PyInstaller...
pyinstaller FactuNabo.spec --noconfirm --clean

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Falló la compilación. Revisa los mensajes anteriores.
    echo Para más información, ejecuta: build_all.bat
    pause
    exit /b %errorlevel%
)

echo.
echo [OK] Ejecutable generado en dist\FactuNabo\
echo.
echo IMPORTANTE: Copia TODA la carpeta dist\FactuNabo\ para distribuir la aplicación.
echo.
pause
