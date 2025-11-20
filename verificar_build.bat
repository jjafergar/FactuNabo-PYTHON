@echo off
REM Script de verificación post-build para FactuNabo
REM Verifica que todos los archivos necesarios estén presentes en dist\FactuNabo\

echo ========================================
echo   Verificación Post-Build - FactuNabo
echo ========================================
echo.

set "BUILD_DIR=dist\FactuNabo"
set "ERRORS=0"

if not exist "%BUILD_DIR%" (
    echo [ERROR] No se encuentra la carpeta %BUILD_DIR%
    echo Ejecuta primero: build_all.bat
    pause
    exit /b 1
)

echo Verificando archivos esenciales...
echo.

REM Verificar ejecutable
if not exist "%BUILD_DIR%\FactuNabo.exe" (
    echo [ERROR] No se encuentra FactuNabo.exe
    set /a ERRORS+=1
) else (
    echo [OK] FactuNabo.exe encontrado
)

REM Verificar carpeta _internal
if not exist "%BUILD_DIR%\_internal" (
    echo [ERROR] No se encuentra la carpeta _internal
    set /a ERRORS+=1
) else (
    echo [OK] Carpeta _internal encontrada
)

REM Verificar archivos de configuración
for %%f in (styles.qss EsquemaProformas.xsd) do (
    if not exist "%BUILD_DIR%\%%f" (
        echo [ERROR] No se encuentra %%f
        set /a ERRORS+=1
    ) else (
        echo [OK] %%f encontrado
    )
)

REM Verificar recursos
if not exist "%BUILD_DIR%\resources" (
    echo [ERROR] No se encuentra la carpeta resources
    set /a ERRORS+=1
) else (
    echo [OK] Carpeta resources encontrada
    if not exist "%BUILD_DIR%\resources\logo.ico" (
        echo [ADVERTENCIA] No se encuentra resources\logo.ico
    ) else (
        echo [OK] resources\logo.ico encontrado
    )
)

REM Verificar plantillas
if not exist "%BUILD_DIR%\Plantillas Facturas" (
    echo [ADVERTENCIA] No se encuentra la carpeta Plantillas Facturas
) else (
    echo [OK] Carpeta Plantillas Facturas encontrada
)

REM Verificar documentación
for %%f in (GUIA_RAPIDA.md MANUAL_USUARIO.md MANUAL_TECNICO.md README.md) do (
    if not exist "%BUILD_DIR%\%%f" (
        echo [ADVERTENCIA] No se encuentra %%f
    ) else (
        echo [OK] %%f encontrado
    )
)

REM Verificar directorios que se crean en runtime
echo.
echo Verificando directorios de runtime...
for %%d in (logs responses backups) do (
    if not exist "%BUILD_DIR%\%%d" (
        echo [INFO] Creando directorio %%d...
        mkdir "%BUILD_DIR%\%%d" 2>nul
    )
    echo [OK] Directorio %%d listo
)

REM Verificar config.ini (opcional, se crea automáticamente)
if exist "%BUILD_DIR%\config.ini" (
    echo [OK] config.ini encontrado (configuración de API guardada)
) else (
    echo [INFO] config.ini no existe (se creará automáticamente al guardar configuración)
)

echo.
echo ========================================
if %ERRORS% EQU 0 (
    echo   Verificación completada: TODO OK
    echo ========================================
    echo.
    echo La aplicación está lista para distribuir.
    echo Copia TODA la carpeta %BUILD_DIR%\ a la ubicación deseada.
) else (
    echo   Verificación completada: %ERRORS% ERROR(ES)
    echo ========================================
    echo.
    echo Revisa los errores anteriores y vuelve a compilar.
)
echo.
pause

