@echo off
REM Script de compilación completa para FactuNabo
REM Genera una carpeta con el ejecutable y todas sus dependencias

echo ========================================
echo   Compilación FactuNabo - Build Folder
echo ========================================
echo.

REM Verificar que estamos en el directorio correcto
if not exist "main.py" (
    echo [ERROR] No se encuentra main.py. Ejecuta este script desde la raíz del proyecto.
    pause
    exit /b 1
)

REM Verificar que PyInstaller está instalado
python -c "import PyInstaller" 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] PyInstaller no está instalado.
    echo Instala las dependencias con: pip install -r requirements-build.txt
    pause
    exit /b 1
)

echo [1/5] Limpiando artefactos anteriores...
if exist build rd /s /q build
if exist dist rd /s /q dist
echo [OK] Limpieza completada
echo.

echo [2/5] Verificando archivos necesarios...
if not exist "FactuNabo.spec" (
    echo [ERROR] No se encuentra FactuNabo.spec
    pause
    exit /b 1
)
if not exist "resources\logo.ico" (
    echo [ADVERTENCIA] No se encuentra resources\logo.ico. El ejecutable no tendrá icono.
)
echo [OK] Archivos verificados
echo.

echo [3/5] Compilando ejecutable...
pyinstaller FactuNabo.spec --noconfirm --clean
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Falló la compilación. Revisa los mensajes anteriores.
    pause
    exit /b %errorlevel%
)
echo [OK] Compilación completada
echo.

echo [4/5] Verificando estructura de salida...
if not exist "dist\FactuNabo\FactuNabo.exe" (
    echo [ERROR] No se generó FactuNabo.exe
    pause
    exit /b 1
)
echo [OK] Ejecutable generado correctamente

REM Verificar y copiar archivos necesarios a la raíz si no están
echo Verificando archivos en la raíz...
if not exist "dist\FactuNabo\styles.qss" (
    echo [ADVERTENCIA] styles.qss no está en la raíz, copiando...
    if exist "styles.qss" (
        copy "styles.qss" "dist\FactuNabo\" >nul
        echo [OK] styles.qss copiado
    ) else (
        echo [ERROR] No se encuentra styles.qss en el proyecto
    )
)

if not exist "dist\FactuNabo\EsquemaProformas.xsd" (
    echo [ADVERTENCIA] EsquemaProformas.xsd no está en la raíz, copiando...
    if exist "EsquemaProformas.xsd" (
        copy "EsquemaProformas.xsd" "dist\FactuNabo\" >nul
        echo [OK] EsquemaProformas.xsd copiado
    ) else (
        echo [ERROR] No se encuentra EsquemaProformas.xsd en el proyecto
    )
)

if not exist "dist\FactuNabo\resources" (
    echo [ADVERTENCIA] resources no está en la raíz, copiando...
    if exist "resources" (
        xcopy "resources" "dist\FactuNabo\resources\" /E /I /Y >nul
        echo [OK] resources copiado
    ) else (
        echo [ERROR] No se encuentra la carpeta resources en el proyecto
    )
)

echo [OK] Verificación de archivos completada
echo.

echo [5/5] Creando directorios necesarios en runtime...
if not exist "dist\FactuNabo\logs" mkdir "dist\FactuNabo\logs"
if not exist "dist\FactuNabo\responses" mkdir "dist\FactuNabo\responses"
if not exist "dist\FactuNabo\backups" mkdir "dist\FactuNabo\backups"
echo [OK] Directorios creados
echo.

echo [INFO] Nota sobre config.ini:
echo   - El archivo config.ini se creará automáticamente al guardar la configuración de API
echo   - Si ya tienes un config.ini con tu configuración, cópialo a dist\FactuNabo\ antes de distribuir
echo.

echo ========================================
echo   Compilación completada exitosamente
echo ========================================
echo.
echo El ejecutable está en: dist\FactuNabo\FactuNabo.exe
echo.
echo IMPORTANTE: Para distribuir la aplicación, copia TODA la carpeta:
echo   dist\FactuNabo\
echo.
echo Esta carpeta contiene:
echo   - FactuNabo.exe (ejecutable principal)
echo   - Todas las dependencias necesarias
echo   - Recursos y plantillas
echo   - Documentación
echo.
echo Tamaño aproximado: 
for /f "tokens=3" %%a in ('dir /s /-c "dist\FactuNabo" ^| find "bytes"') do set size=%%a
echo   %size% bytes
echo.
pause
