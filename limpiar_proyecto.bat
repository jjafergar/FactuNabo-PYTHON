@echo off
REM Script para limpiar archivos temporales y de desarrollo del proyecto FactuNabo

echo ========================================
echo   Limpieza del Proyecto FactuNabo
echo ========================================
echo.
echo Este script eliminará:
echo   - Carpetas __pycache__ (archivos compilados de Python)
echo   - Carpeta build/ (archivos temporales de compilación)
echo   - Carpeta dist/ (si existe, archivos de distribución)
echo   - Logs de desarrollo (logs/*.log, logs/*.xml)
echo   - Respuestas de pruebas (responses/*.json, responses/*.xml)
echo   - Backups (backups/*)
echo   - Archivos temporales de Excel (~$*.xlsm)
echo   - Base de datos de desarrollo (factunabo_history.db)
echo   - Archivo de usuarios de desarrollo (users.json)
echo   - Archivo spec antiguo (main.spec)
echo   - Logo no usado (logoapp.jpg)
echo.
set /p confirm="¿Continuar con la limpieza? (S/N): "
if /i not "%confirm%"=="S" (
    echo Limpieza cancelada.
    pause
    exit /b 0
)
echo.
echo [1/8] Eliminando carpetas __pycache__...
for /d /r . %%d in (__pycache__) do @if exist "%%d" (
    echo   Eliminando: %%d
    rd /s /q "%%d" 2>nul
)
echo [OK] Carpetas __pycache__ eliminadas
echo.

echo [2/8] Eliminando carpeta build/...
if exist build (
    rd /s /q build 2>nul
    echo [OK] Carpeta build/ eliminada
) else (
    echo [INFO] Carpeta build/ no existe
)
echo.

echo [3/8] Eliminando carpeta dist/...
if exist dist (
    rd /s /q dist 2>nul
    echo [OK] Carpeta dist/ eliminada
) else (
    echo [INFO] Carpeta dist/ no existe
)
echo.

echo [4/8] Limpiando logs de desarrollo...
if exist logs (
    del /q logs\*.log 2>nul
    del /q logs\*.xml 2>nul
    del /q logs\*.jsonl 2>nul
    echo [OK] Logs eliminados
) else (
    echo [INFO] Carpeta logs/ no existe
)
echo.

echo [5/8] Limpiando respuestas de pruebas...
if exist responses (
    del /q responses\*.json 2>nul
    del /q responses\*.xml 2>nul
    echo [OK] Respuestas eliminadas
) else (
    echo [INFO] Carpeta responses/ no existe
)
echo.

echo [6/8] Limpiando backups...
if exist backups (
    del /q backups\*.* 2>nul
    echo [OK] Backups eliminados
) else (
    echo [INFO] Carpeta backups/ no existe
)
echo.

echo [7/8] Eliminando archivos temporales...
del /q "~$*.xlsm" 2>nul
del /q "~$*.xlsx" 2>nul
del /q "*.tmp" 2>nul
del /q "*.temp" 2>nul
echo [OK] Archivos temporales eliminados
echo.

echo [8/8] Eliminando archivos de desarrollo...
if exist factunabo_history.db (
    del /q factunabo_history.db 2>nul
    echo [OK] factunabo_history.db eliminado
)
if exist users.json (
    del /q users.json 2>nul
    echo [OK] users.json eliminado
)
if exist main.spec (
    del /q main.spec 2>nul
    echo [OK] main.spec eliminado (usamos FactuNabo.spec)
)
if exist logoapp.jpg (
    del /q logoapp.jpg 2>nul
    echo [OK] logoapp.jpg eliminado (usamos resources/logo.ico)
)
echo.

echo ========================================
echo   Limpieza completada
echo ========================================
echo.
echo Archivos eliminados:
echo   - Carpetas __pycache__ regeneradas automáticamente
echo   - Carpeta build/ se regenera al compilar
echo   - Logs, responses y backups se recrean al usar la aplicación
echo   - Base de datos y usuarios se recrean al iniciar la aplicación
echo.
echo NOTA: Los archivos eliminados se regeneran automáticamente
echo       cuando ejecutes la aplicación o compiles el proyecto.
echo.
pause

