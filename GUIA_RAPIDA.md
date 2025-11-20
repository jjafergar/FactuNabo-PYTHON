# 🚀 Guía Rápida - FactuNabo

Guía paso a paso para emitir facturas con FactuNabo de forma rápida y sencilla.

---

## 📋 Paso 1: Preparar el Excel

### 1.1. Abrir tu Excel de facturas

Abre el archivo Excel donde tienes tus facturas (por ejemplo: `Resumen FRAs 2025.xlsm`).

### 1.2. Localizar la factura a emitir

Busca la factura que quieres emitir en cualquiera de estas hojas:
- **Resumen**
- **Valcabado**
- **FP Lux**
- **Piquito Ole**
- O cualquier otra hoja donde tengas tus facturas

### 1.3. Copiar la fila completa de la factura

1. **Selecciona toda la fila** de la factura que quieres emitir
   - Haz clic en el número de fila (a la izquierda) para seleccionar toda la fila
   - O selecciona todas las celdas de la fila (Ctrl + Shift + →)

2. **Copia la fila** (Ctrl + C)

### 1.4. Pegar en la hoja "Macro"

1. Ve a la hoja **"Macro"** (o **"MACRO"**)
2. **Pega la fila** en la primera fila vacía (Ctrl + V)
3. Asegúrate de que la fila esté completa y los datos se hayan pegado correctamente

### 1.5. Guardar el Excel

Guarda el archivo Excel (Ctrl + S)

> 💡 **Consejo**: Puedes copiar varias facturas a la vez. Simplemente copia todas las filas que necesites y pégalas en la hoja Macro, una debajo de otra.

---

## 📂 Paso 2: Abrir FactuNabo

1. Localiza el archivo **`FactuNabo.exe`** en tu carpeta
2. **Doble clic** para abrir la aplicación
3. Si aparece la pantalla de login, introduce tu usuario y contraseña

---

## 📁 Paso 3: Cargar el Excel en FactuNabo

1. En el menú lateral izquierdo, haz clic en **"📁 Cargar Excel"**
2. Tienes dos opciones:
   - **Opción A**: Haz clic en **"Seleccionar Excel"** y busca tu archivo
   - **Opción B**: **Arrastra** el archivo Excel directamente a la zona indicada
3. Espera a que se cargue y valide el archivo

---

## ✅ Paso 4: Revisar las Facturas

Una vez cargado el Excel, verás una tabla con todas las facturas que has pegado en la hoja Macro.

### Revisa que todo esté correcto:

- ✅ **Número de factura** correcto
- ✅ **Cliente** correcto
- ✅ **Importe** correcto
- ✅ **Fecha** correcta
- ✅ **Validación NIF**: Debe aparecer "✅ NIF Correcto" (verde)

> ⚠️ **Si aparece "❌ NIF Incorrecto"**: Revisa el NIF del cliente en el Excel y corrígelo.

---

## 🚀 Paso 5: Enviar las Facturas

1. En el menú lateral, haz clic en **"📤 Enviar Facturas"**
2. Verás una tabla de **"Previsualización de Facturas a Enviar"** con todas las facturas que se van a enviar
3. Revisa que todo esté correcto
4. Haz clic en el botón **"▶️ Enviar Facturas"**
5. Espera a que termine el proceso (verás un progreso en pantalla)

---

## 📊 Paso 6: Revisar los Resultados

Una vez terminado el envío, verás la tabla **"Resultados del Envío"** con el estado de cada factura:

- ✅ **ÉXITO**: La factura se envió correctamente
- ⚠️ **DUPLICADO**: La factura ya existe en Facturantia
- ❌ **ERROR**: Hubo un problema (revisa los detalles)

### Descargar PDFs

Si las facturas se enviaron correctamente, puedes descargar los PDFs:
- Haz clic en el botón **"📄"** (Ver) en la columna "Ver Factura" de cada factura exitosa

---

## 🔄 ¿Necesitas Rectificar una Factura?

Si necesitas rectificar una factura ya emitida:

1. En la tabla de **"Cargar Excel"**, haz clic en la **fila** de la factura que quieres rectificar
2. Haz clic en el botón **"🔄 Rectificativa Asistida"** que aparece
3. El asistente te guiará para:
   - Identificar qué cambió (importes, conceptos, cliente, etc.)
   - Seleccionar el tipo de rectificación (R1, R4, etc.)
   - Configurar los datos de la rectificativa
4. Haz clic en **"Aceptar"**
5. La factura aparecerá marcada con un círculo verde 🔵 indicando que es una rectificativa
6. Sigue los pasos 5 y 6 para enviar la rectificativa

---

## ⚙️ Configuración Inicial (Solo la Primera Vez)

### Configurar la API de Facturantia

1. En el menú lateral, haz clic en **"⚙️ Configuración"**
2. En la sección **"Conexión API"**, haz clic en **"⚙️ Configurar Parámetros API"**
3. Introduce:
   - **URL de API**: `https://www.facturantia.com/API/proformas_receptor.php`
   - **Token**: Tu token de Facturantia
   - **Usuario**: Tu email de usuario
   - **Timeout (seg)**: `30` (o el que te indiquen)
4. Haz clic en **"Guardar"**

> 💡 **Nota**: Esta configuración se guarda automáticamente. No tendrás que volver a introducirla.

---

## ❓ Preguntas Frecuentes

### ¿Puedo enviar varias facturas a la vez?

**Sí**. Simplemente copia todas las filas de facturas que necesites en la hoja Macro, una debajo de otra, y envíalas todas juntas.

### ¿Qué hago si aparece un error de NIF?

Revisa el NIF del cliente en el Excel y corrígelo. Luego vuelve a cargar el Excel en FactuNabo.

### ¿Puedo modificar una factura después de cargarla?

No directamente en FactuNabo. Debes modificar el Excel, guardarlo, y volver a cargarlo en FactuNabo.

### ¿Qué pasa si una factura ya existe en Facturantia?

Aparecerá como **"DUPLICADO"** en los resultados. No se enviará de nuevo.

### ¿Cómo sé qué facturas se enviaron correctamente?

En la tabla de **"Resultados del Envío"**, las facturas con estado **"ÉXITO"** se enviaron correctamente.

### ¿Dónde se guardan los PDFs descargados?

Los PDFs se guardan en la carpeta que configures en **Configuración → Destino de PDFs**. Por defecto, se descargan manualmente desde la tabla de resultados.

---

## 📞 ¿Necesitas Ayuda?

Si tienes problemas o dudas:

1. Revisa el **MANUAL_USUARIO.md** para información más detallada
2. Revisa el **MANUAL_TECNICO.md** si eres técnico
3. Contacta con el administrador del sistema

---

**¡Listo! Ya sabes cómo usar FactuNabo de forma rápida y sencilla.** 🎉

