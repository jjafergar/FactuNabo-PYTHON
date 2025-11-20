# 📊 Estado Actual de la Aplicación FactuNabo

**Fecha de actualización**: Noviembre 2025  
**Versión**: 2.0

---

## 🎯 Funcionalidades Implementadas

### ✅ Interfaz de Usuario

- **Diseño moderno**: Interfaz inspirada en iOS 26 con efectos de transparencia y animaciones suaves
- **Temas**: Modo claro y modo oscuro con paleta de colores corporativa (verde `#A0BF6E`)
- **Responsive**: Adaptación automática a diferentes tamaños de pantalla
- **Animaciones**: Transiciones suaves entre páginas y efectos hover en botones
- **Glassmorphism**: Efectos de vidrio esmerilado en tarjetas y paneles

### ✅ Gestión de Usuarios

- Sistema de autenticación con usuarios y contraseñas
- Almacenamiento seguro de credenciales (hash SHA-256)
- Gestión de usuarios desde el panel de configuración:
  - Añadir nuevos usuarios
  - Cambiar contraseñas
  - Eliminar usuarios (excepto "admin")

### ✅ Carga y Validación de Excel

- **Carga de archivos**: Arrastrar y soltar o selección manual
- **Validación automática**: Verificación de estructura y datos antes del envío
- **Validación de NIF/CIF/NIE**: Validación automática con indicadores visuales (verde/rojo)
- **Vista previa**: Tabla interactiva con todas las facturas cargadas
- **Búsqueda**: Filtrado en tiempo real de facturas
- **Vista compacta**: Opción para ver más datos en menos espacio
- **Advertencias pre-envío**: Aviso si hay NIFs incorrectos antes de enviar

### ✅ Envío de Facturas

- **Proceso automatizado**: Envío masivo de facturas a la API de Facturantia
- **Indicador de progreso**: Barra de progreso y pasos visuales (Stepper)
- **Validación XSD**: Validación del XML generado antes del envío
- **Gestión de errores**: Manejo robusto de errores con mensajes claros
- **Resultados detallados**: Estados por factura (Éxito, Duplicado, Error)
- **Previsualización mejorada**: Tabla con Factura, Fecha, Empresa, Cliente, Concepto, Importe Total
- **Número asignado por Facturantia**: Uso del número real asignado en lugar del número original

### ✅ Histórico de Envíos

- **Base de datos local**: Almacenamiento SQLite de todos los envíos
- **Consultas avanzadas**: Filtrado por empresa emisora y período
- **Estadísticas**: Dashboard con métricas clave:
  - Total de facturas enviadas
  - Facturas exitosas
  - Facturado del mes
  - Envíos del mes
- **Actualización manual**: Botón para refrescar datos

### ✅ Descarga de PDFs

- **Descarga automática**: Opción para descargar PDFs después del envío
- **Descarga manual**: Botón para descargar PDFs de envíos anteriores
- **Nomenclatura inteligente**: `[Número] - [Cliente] - [Importe].pdf`
- **Navegadores soportados**: Chrome y Edge (modo headless)

### ✅ Configuración

- **API**: Configuración de URL, Token y Usuario
- **Usuarios**: Gestión completa de usuarios del sistema
- **Historial**: Opción para borrar el historial completo
- **Temas**: Modo claro y oscuro con aplicación completa a todos los componentes
- **Drop zone adaptativo**: Zona de arrastre que se adapta al tema seleccionado

---

## 🔧 Características Técnicas

### Procesamiento de Facturas

- **Soporte múltiples emisores**: Un Excel puede contener facturas de varias empresas
- **Detección automática de tipos**:
  - Facturas normales
  - Facturas de intereses (prefijo "Int")
  - Facturas intracomunitarias (prefijo "A")
  - Facturas rectificativas (R1, R2, R3, R4, R5) con asistente inteligente:
    - Detección automática de cambios
    - Sugerencias de tipo y motivo
    - Soporte para rectificativas de años anteriores
    - Carga automática de Excel histórico
- **Cálculo automático de IVA**: Basado en base imponible y total
- **Gestión de retenciones**: IRPF 19% para intereses y series configuradas
- **Normalización de datos**: Limpieza automática de NIFs, CIFs, fechas

### Validaciones Implementadas

- ✅ Validación de estructura del Excel
- ✅ Validación de campos obligatorios
- ✅ Validación de formatos (fechas, números)
- ✅ Validación de IBAN (obligatorio)
- ✅ **Validación de NIF/CIF/NIE**: Validación automática de documentos de identificación
  - NIF español (8 dígitos + letra)
  - CIF español (letra + 7 dígitos + carácter)
  - NIE español (X/Y/Z + 7 dígitos + letra)
  - NIF-IVA para países de la UE (cualquier código de país de 2 letras)
  - Validación especial para facturas no comunitarias (NC)
- ✅ Validación XSD antes del envío
- ✅ Detección de duplicados
- ✅ Validación de facturas rectificativas
- ✅ Validación de campos obligatorios del cliente (provincia, población, domicilio, CP)

### Integración con API

- **Endpoint configurable**: URL personalizable por emisor
- **Autenticación**: Token y usuario por emisor
- **Timeout configurable**: Tiempo de espera ajustable
- **Manejo de respuestas**: Procesamiento de respuestas de la API
- **Logging completo**: Registro de todas las operaciones

---

## 📋 Estructura de Datos

### Excel de Entrada

**Hoja "Macro"**:
- Columnas A-Z: Datos de facturas y conceptos
- Columnas AA-AI: Información adicional (gastos, IBAN, estado, etc.)

**Hoja "CLIENTES"**:
- Configuración de empresas emisoras
- Credenciales de API por emisor
- IBANs por defecto
- Configuración de retenciones

### Base de Datos Local

**Tabla `envios`**:
- Registro de todos los envíos realizados
- Estados: ÉXITO, DUPLICADO, ERROR
- Fechas y timestamps
- Información de facturas enviadas

---

## 🎨 Mejoras de Interfaz Implementadas

### Diseño Visual

- ✅ Paleta de colores corporativa (verde `#A0BF6E`)
- ✅ Efectos de transparencia (glassmorphism)
- ✅ Sombras suaves y modernas
- ✅ Bordes redondeados en tablas y tarjetas
- ✅ Iconos y emojis para mejor UX

### Interactividad

- ✅ Animaciones hover en botones (crecimiento y oscurecimiento)
- ✅ Transiciones suaves entre páginas
- ✅ Efectos de elevación en botones principales
- ✅ Feedback visual en todas las acciones

### Accesibilidad

- ✅ Modo oscuro completo
- ✅ Contraste adecuado en ambos temas
- ✅ Tamaños de fuente legibles
- ✅ Espaciado cómodo entre elementos

---

## ⚠️ Limitaciones Conocidas

1. **Formato Excel**: Solo soporta `.xlsx` (no `.xls` antiguo)
2. **Navegadores PDF**: Requiere Chrome o Edge instalados
3. **Sistema Operativo**: Optimizado para Windows 10/11
4. **Tamaño de Excel**: Archivos muy grandes (>10.000 filas) pueden ser lentos

---

## 🔄 Flujo de Trabajo Típico

```
1. Usuario inicia sesión
   ↓
2. Configura API (si es primera vez)
   ↓
3. Carga Excel con facturas
   ↓
4. Sistema valida estructura y datos
   ↓
5. Usuario revisa vista previa
   ↓
6. Usuario inicia envío
   ↓
7. Sistema genera XMLs y valida XSD
   ↓
8. Sistema envía a API de Facturantia
   ↓
9. Sistema marca resultados (Éxito/Duplicado/Error)
   ↓
10. Sistema actualiza Excel (marca estado en columna AC)
   ↓
11. Sistema guarda en historial local
   ↓
12. Usuario puede descargar PDFs (opcional)
```

---

## 📝 Notas de Desarrollo

### Tecnologías Utilizadas

- **Python 3.8+**: Lenguaje principal
- **PySide6**: Framework GUI
- **Pandas**: Procesamiento de datos Excel
- **OpenPyXL**: Lectura/escritura de Excel
- **Requests**: Comunicación HTTP con API
- **XMLSchema**: Validación de XML
- **SQLite**: Base de datos local

### Arquitectura

- **MVC simplificado**: Separación de lógica y presentación
- **Worker Thread**: Procesamiento en segundo plano
- **Signals/Slots**: Comunicación asíncrona
- **QSS**: Estilos centralizados

---

## 🚀 Próximas Mejoras Sugeridas

### Funcionalidades

- [x] Validación de NIF/CIF/NIE
- [x] Asistente de rectificativas mejorado
- [x] Rectificativas de años anteriores
- [x] Previsualización con conceptos
- [ ] Exportación de historial a Excel/CSV (parcialmente implementado para resultados)
- [ ] Búsqueda avanzada en histórico
- [ ] Plantillas de Excel preconfiguradas
- [ ] Notificaciones de errores por email
- [ ] Modo offline con cola de envíos

### Interfaz

- [x] Modo oscuro completo con adaptación de todos los componentes
- [x] Drop zone adaptativo al tema
- [ ] Iconos SVG personalizados (reemplazar emojis)
- [x] Selector de color de acento (implementado)
- [ ] Más opciones de personalización
- [ ] Atajos de teclado
- [x] Tooltips informativos (implementados en validación NIF)

### Rendimiento

- [ ] Caché de validaciones
- [ ] Procesamiento paralelo de facturas
- [ ] Compresión de logs antiguos
- [ ] Optimización de consultas SQL

---

## 📞 Soporte

Para reportar problemas o solicitar nuevas funcionalidades, contacta con el equipo de desarrollo.

---

**Documento generado automáticamente**  
**Versión de la aplicación**: 2.0

