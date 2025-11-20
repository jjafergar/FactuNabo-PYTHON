# 📦 Guía de Compilación - FactuNabo

Esta guía explica cómo compilar FactuNabo en un ejecutable (.exe) con todas sus dependencias.

## 📋 Requisitos Previos

1. **Python 3.10 o superior** instalado en Windows
2. **Git** (opcional, solo si clonas el repositorio)
3. **Espacio en disco**: Al menos 1 GB libre

## 🚀 Proceso de Compilación

### Paso 1: Preparar el Entorno

1. Abre PowerShell o CMD en la raíz del proyecto
2. Crea y activa un entorno virtual (recomendado):
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\activate
   ```

### Paso 2: Instalar Dependencias

Instala las dependencias necesarias para compilar:

```powershell
pip install -r requirements-build.txt
```

O si prefieres instalar todas las dependencias (incluyendo opcionales):

```powershell
pip install -r requirements.txt
```

### Paso 3: Verificar Archivos Necesarios

Asegúrate de que existan estos archivos:
- ✅ `main.py` (archivo principal)
- ✅ `FactuNabo.spec` (configuración de PyInstaller)
- ✅ `resources/logo.ico` (icono del ejecutable)
- ✅ `styles.qss` (estilos de la aplicación)
- ✅ `EsquemaProformas.xsd` (esquema de validación XML)

### Paso 4: Compilar

Ejecuta el script de compilación:

```powershell
.\build_all.bat
```

O manualmente:

```powershell
pyinstaller FactuNabo.spec --noconfirm --clean
```

### Paso 5: Verificar Resultado

Después de la compilación, puedes verificar automáticamente que todo esté correcto:

```powershell
.\verificar_build.bat
```

Este script verifica que todos los archivos necesarios estén presentes.

O verifica manualmente que se haya creado:

```
dist/
└── FactuNabo/
    ├── FactuNabo.exe          ← Ejecutable principal
    ├── _internal/             ← Dependencias y librerías
    ├── resources/             ← Recursos (iconos, etc.)
    ├── Plantillas Facturas/   ← Plantillas Word
    ├── styles.qss             ← Estilos
    ├── EsquemaProformas.xsd   ← Esquema XML
    ├── *.md                   ← Documentación (GUIA_RAPIDA.md, MANUAL_USUARIO.md, etc.)
    ├── config.ini             ← Configuración de API (se crea automáticamente)
    ├── logs/                  ← Directorio para logs (vacío)
    └── responses/             ← Directorio para respuestas (vacío)
```

**Nota**: El script `build_all.bat` verifica automáticamente que los archivos `styles.qss`, `EsquemaProformas.xsd` y `resources/` estén en la raíz y los copia si faltan.

## 📦 Distribución

Para distribuir la aplicación:

1. **Copia TODA la carpeta** `dist\FactuNabo\` a la ubicación deseada
2. **No copies solo el .exe**, necesita toda la carpeta para funcionar
3. El usuario final puede ejecutar `FactuNabo.exe` directamente

### Estructura Mínima Requerida

La carpeta `dist\FactuNabo\` debe contener:
- `FactuNabo.exe` (obligatorio)
- Carpeta `_internal/` (obligatorio, contiene dependencias)
- `resources/` (obligatorio, contiene iconos)
- `styles.qss` (obligatorio)
- `EsquemaProformas.xsd` (obligatorio)
- `Plantillas Facturas/` (opcional, pero recomendado)
- Documentación `.md` (opcional)
- `config.ini` (se crea automáticamente al guardar configuración de API)

**Nota importante sobre `config.ini`**:
- Este archivo se crea automáticamente cuando el usuario guarda la configuración de API por primera vez
- Si ya tienes un `config.ini` con tu configuración, puedes copiarlo a `dist\FactuNabo\` antes de distribuir
- Esto permite distribuir la aplicación ya preconfigurada con URL, Token, Usuario y Timeout

## 🔧 Configuración Avanzada

### Modificar el Archivo .spec

El archivo `FactuNabo.spec` contiene la configuración de PyInstaller. Puedes modificarlo para:

- **Añadir archivos adicionales**: Edita la lista `data_files`
- **Excluir módulos**: Añade a la lista `excludes` para reducir tamaño
- **Incluir módulos ocultos**: Añade a `hiddenimports` si PyInstaller no los detecta
- **Cambiar el icono**: Modifica la ruta en `icon=`

### Reducir el Tamaño del Ejecutable

Para reducir el tamaño:

1. **Limpiar logs antes de compilar**:
   ```powershell
   rd /s /q logs
   rd /s /q responses
   ```

2. **Usar `requirements-build.txt`** en lugar de `requirements.txt` (solo dependencias esenciales)

3. **Excluir módulos no usados** en `FactuNabo.spec` (ya configurado)

4. **Comprimir con UPX** (ya habilitado en el .spec, pero requiere UPX instalado)

## ⚠️ Problemas Comunes

### Error: "No module named 'xxx'"

**Solución**: Añade el módulo a `hiddenimports` en `FactuNabo.spec` o instálalo con pip.

### Error: "Failed to execute script"

**Solución**: 
1. Ejecuta desde CMD para ver el error completo
2. Verifica que todos los archivos en `data_files` existan
3. Revisa los logs en `build\FactuNabo\warn-FactuNabo.txt`

### Error: "timestamp too large to convert to C PyTime_t"

**Solución**: 
- Este error ha sido corregido en las últimas versiones
- Asegúrate de tener la versión más reciente del código
- Si persiste, verifica que las fechas en el Excel estén en formato correcto (1900-2100)

### El ejecutable no encuentra recursos

**Solución**: 
- Verifica que `resource_path()` en `app/core/resources.py` funciona correctamente
- Asegúrate de que los archivos estén en `data_files` del .spec
- El script `build_all.bat` copia automáticamente los archivos si faltan

### Archivos faltantes en dist/FactuNabo/ (styles.qss, EsquemaProformas.xsd, resources/)

**Solución**:
- El script `build_all.bat` verifica y copia automáticamente estos archivos
- Si faltan después de compilar, ejecuta `build_all.bat` de nuevo
- Verifica que los archivos existan en la raíz del proyecto antes de compilar

### El ejecutable es muy grande (>200 MB)

**Solución**:
- Es normal para aplicaciones con PySide6
- Usa `requirements-build.txt` para instalar solo lo necesario
- Excluye módulos no usados (ya configurado)

## 📝 Notas Importantes

1. **Primera ejecución**: El primer arranque puede ser lento mientras PyInstaller descomprime recursos
2. **Antivirus**: Algunos antivirus pueden marcar el .exe como sospechoso. Es un falso positivo común con PyInstaller
3. **Windows Defender**: Puede requerir permisos de administrador en la primera ejecución
4. **Rutas**: La aplicación usa rutas relativas, no muevas archivos individuales fuera de la carpeta

## 🧹 Limpiar el Proyecto

Antes de compilar, puedes limpiar archivos temporales y de desarrollo:

```powershell
.\limpiar_proyecto.bat
```

Este script elimina:
- Carpetas `__pycache__` (archivos compilados de Python)
- Carpeta `build/` (archivos temporales de compilación)
- Logs, responses y backups de desarrollo
- Archivos temporales y obsoletos

**Nota**: Los archivos eliminados se regeneran automáticamente al ejecutar la aplicación o compilar.

## 🔄 Actualizar la Compilación

Para recompilar después de cambios:

1. (Opcional) Limpia artefactos anteriores:
   ```powershell
   .\limpiar_proyecto.bat
   ```
   O manualmente:
   ```powershell
   rd /s /q build dist
   ```

2. Vuelve a ejecutar `build_all.bat`

## 📞 Soporte

Si encuentras problemas durante la compilación:

1. Revisa los logs en `build\FactuNabo\`
2. Verifica que todas las dependencias estén instaladas
3. Asegúrate de usar Python 3.10 o superior
4. Consulta la documentación de PyInstaller: https://pyinstaller.org/

## 📋 Scripts Disponibles

El proyecto incluye varios scripts útiles:

- **`build_all.bat`**: Compilación completa con verificación automática de archivos
- **`verificar_build.bat`**: Verifica que todos los archivos necesarios estén en `dist/FactuNabo/`
- **`limpiar_proyecto.bat`**: Limpia archivos temporales y de desarrollo
- **`build.bat`**: Script simplificado que llama a `build_all.bat`

---

**Última actualización**: Noviembre 2025  
**Versión**: 2.0

