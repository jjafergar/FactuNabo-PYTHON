# FactuNabo
Programa para emitir Facturas vía API.

## 📚 Documentación

- **[GUIA_RAPIDA.md](GUIA_RAPIDA.md)** - Guía rápida paso a paso para empezar a usar FactuNabo
- **[MANUAL_USUARIO.md](MANUAL_USUARIO.md)** - Manual completo de usuario con todas las funcionalidades
- **[MANUAL_TECNICO.md](MANUAL_TECNICO.md)** - Manual técnico para desarrolladores
- **[GUIA_COMPILACION.md](GUIA_COMPILACION.md)** - Guía completa para compilar el proyecto a ejecutable (.exe)

## Construir ejecutable (.exe)

### Compilación Rápida

1. **Preparar entorno**
   - Instala Python 3.10+ en Windows
   - Crea y activa un entorno virtual:
     ```powershell
     python -m venv .venv
     .\.venv\Scripts\activate
     ```
   - Instala dependencias de compilación:
     ```powershell
     pip install -r requirements-build.txt
     ```

2. **Compilar**
   - Ejecuta el script de compilación completa:
     ```powershell
     .\build_all.bat
     ```
   - O para compilación rápida:
     ```powershell
     .\build.bat
     ```

3. **Verificar**
   - Verifica que todo esté correcto:
     ```powershell
     .\verificar_build.bat
     ```

4. **Distribuir**
   - El ejecutable quedará en `dist\FactuNabo\FactuNabo.exe`
   - **IMPORTANTE**: Copia **TODA** la carpeta `dist\FactuNabo\` cuando distribuyas la aplicación
   - No copies solo el .exe, necesita toda la carpeta para funcionar
   - **Configuración portable**: El archivo `config.ini` (configuración de API) se crea automáticamente al guardar. Si ya tienes uno configurado, cópialo a `dist\FactuNabo\` antes de distribuir

### Documentación Completa

Para más detalles sobre la compilación, consulta: **[GUIA_COMPILACION.md](GUIA_COMPILACION.md)**

## Recomendaciones de rendimiento

- **Limpiar logs antes de compilar:** vacía la carpeta `logs/` para reducir el tamaño del paquete.
- **Mantener requirements mínimos:** elimina dependencias no utilizadas del `requirements.txt` antes de instalar.
- **Usar `--clean`:** el script ya lo hace para quitar artefactos intermedios.
- **Verificar rutas relativas:** el código usa `resource_path()` para localizar recursos, así que no hagas referencias absolutas en nuevos módulos.

## Soporte
Para dudas sobre la API de Facturantia (por ejemplo, caducidad de certificados), contacta con su equipo de soporte y actualiza `FactuNabo.spec` / `main.py` con los endpoints que te indiquen.
