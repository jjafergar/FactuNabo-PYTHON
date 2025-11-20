# -*- coding: utf-8 -*-
"""
Módulo para generar archivos .mmb (formato de ancho fijo para importación contable)
"""
import os
import re
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from pathlib import Path

from app.core.logging import get_logger
from app.services.database import fetch_all
import macro_adapter
import prueba

logger = get_logger("services.generador_mmb")


def obtener_datos_factura_desde_xml(xml_path: str) -> Optional[Dict]:
    """Extrae datos de una factura desde su XML guardado"""
    try:
        if not os.path.exists(xml_path):
            return None
        
        tree = ET.parse(xml_path)
        root = tree.getroot()
        
        # Buscar datos en el XML
        datos = {}
        
        # Fecha de emisión
        fecha_elem = root.find(".//fecha_emision")
        if fecha_elem is not None and fecha_elem.text:
            datos['fecha_emision'] = fecha_elem.text
        
        # Cliente
        cliente = root.find(".//cliente")
        if cliente is not None:
            nombre_elem = cliente.find("nombre")
            if nombre_elem is not None and nombre_elem.text:
                datos['cliente_nombre'] = nombre_elem.text.strip()
            
            doc_elem = cliente.find("numero_documento")
            if doc_elem is not None and doc_elem.text:
                datos['cliente_nif'] = doc_elem.text.strip()
        
        # Conceptos para calcular base e IVA
        conceptos = root.findall(".//concepto")
        base_total = 0.0
        iva_total = 0.0
        iva_porcentaje = 21.0  # Por defecto
        
        for concepto in conceptos:
            # Intentar obtener base desde múltiples campos
            base_elem = concepto.find("base_imponible") or concepto.find("base") or concepto.find("importe_bruto")
            if base_elem is not None and base_elem.text:
                try:
                    base_str = base_elem.text.replace(",", ".").strip()
                    if base_str:
                        base = float(base_str)
                        base_total += base
                except (ValueError, AttributeError):
                    pass
            
            # Porcentaje IVA
            porcentaje_elem = concepto.find("porcentaje")
            if porcentaje_elem is not None and porcentaje_elem.text:
                try:
                    porc_str = porcentaje_elem.text.replace(",", ".").strip()
                    if porc_str:
                        iva_porcentaje = float(porc_str)
                except (ValueError, AttributeError):
                    pass
            
            # Cuota IVA - buscar específicamente en elementos de IVA
            # NO usar "importe" del concepto porque puede ser el importe total, no el IVA
            cuota_elem = concepto.find("cuota")
            if cuota_elem is not None and cuota_elem.text:
                try:
                    cuota_str = cuota_elem.text.replace(",", ".").strip()
                    if cuota_str:
                        cuota = float(cuota_str)
                        iva_total += cuota
                        logger.debug(f"IVA encontrado en concepto: {cuota}")
                except (ValueError, AttributeError):
                    pass
        
        # También intentar obtener desde resumen de impuestos
        resumen_iva = root.find(".//impuestos_repercutidos")
        if resumen_iva is not None:
            for impuesto in resumen_iva.findall(".//impuesto_repercutido"):
                base_elem = impuesto.find("base_imponible")
                if base_elem is not None and base_elem.text:
                    try:
                        base_str = base_elem.text.replace(",", ".").strip()
                        if base_str:
                            base_total += float(base_str)
                    except (ValueError, AttributeError):
                        pass
                
                cuota_elem = impuesto.find("cuota")
                if cuota_elem is not None and cuota_elem.text:
                    try:
                        cuota_str = cuota_elem.text.replace(",", ".").strip()
                        if cuota_str:
                            iva_total += float(cuota_str)
                    except (ValueError, AttributeError):
                        pass
        
        # Intentar obtener total desde el XML
        total_elem = root.find(".//importe_total") or root.find(".//total")
        total_xml = 0.0
        if total_elem is not None and total_elem.text:
            try:
                total_str = total_elem.text.replace(",", ".").strip()
                if total_str:
                    total_xml = float(total_str)
            except (ValueError, AttributeError):
                pass
        
        # Si tenemos total pero no base, calcular base desde total
        if base_total == 0.0 and total_xml > 0:
            if iva_porcentaje > 0:
                base_total = total_xml / (1 + iva_porcentaje / 100.0)
                iva_total = total_xml - base_total
            else:
                base_total = total_xml
        
        datos['base_imponible'] = base_total
        datos['iva_importe'] = iva_total
        datos['iva_porcentaje'] = iva_porcentaje
        
        # Logging detallado para diagnóstico
        logger.debug(f"XML {xml_path}: base={base_total}, IVA_importe={iva_total}, IVA_%={iva_porcentaje}, total={total_xml}")
        # Usar total calculado o el del XML
        datos['total'] = total_xml if total_xml > 0 else (base_total + iva_total)
        
        # Número de factura
        num_elem = root.find(".//numero_factura")
        if num_elem is not None and num_elem.text:
            datos['num_factura'] = num_elem.text.strip()
        
        # Serie de factura (para detectar intracomunitarias)
        serie_elem = root.find(".//serie_factura")
        if serie_elem is not None and serie_elem.text:
            datos['serie_factura'] = serie_elem.text.strip()
        
        return datos
    except Exception as e:
        logger.warning(f"Error leyendo XML {xml_path}: {e}")
        return None


def buscar_xml_factura(num_factura: str, empresa: str, logs_dir: str = "logs", responses_dir: str = "responses") -> Optional[str]:
    """Busca el archivo XML de una factura en los directorios de logs y responses"""
    # Normalizar nombre de empresa para búsqueda
    empresa_safe = str(empresa).replace(" ", "_").replace(".", "")
    num_safe = str(num_factura).replace("/", "_")
    
    # Buscar en logs
    if os.path.exists(logs_dir):
        for archivo in os.listdir(logs_dir):
            if archivo.endswith(".xml") and empresa_safe in archivo and num_safe in archivo:
                return os.path.join(logs_dir, archivo)
    
    # Buscar en responses
    if os.path.exists(responses_dir):
        for archivo in os.listdir(responses_dir):
            if archivo.endswith(".xml") and num_safe in archivo:
                return os.path.join(responses_dir, archivo)
    
    return None


def obtener_codigo_cliente_contable(cliente_nif: str) -> str:
    """
    Genera o busca el código de cliente contable basado en el NIF.
    Por defecto, genera un código de 11 dígitos basado en el NIF.
    """
    if not cliente_nif:
        return "00000000000"
    
    # Limpiar NIF (quitar espacios y guiones)
    nif_limpio = re.sub(r'[^A-Z0-9]', '', cliente_nif.upper())
    
    # Si es un NIF español (8 dígitos + letra), usar los dígitos
    if len(nif_limpio) >= 8 and nif_limpio[:8].isdigit():
        # Generar código de 11 dígitos: 430 + 8 dígitos del NIF
        codigo = "430" + nif_limpio[:8]
        return codigo.ljust(11, "0")[:11]
    
    # Si no, generar un hash numérico simple
    hash_val = abs(hash(nif_limpio)) % 100000000
    return f"430{str(hash_val).zfill(8)}"[:11]


def formatear_campo_fijo(valor: str, longitud: int, alineacion: str = "izquierda") -> str:
    """Formatea un campo con ancho fijo"""
    if valor is None:
        valor = ""
    
    valor_str = str(valor).strip()
    
    if alineacion == "derecha":
        return valor_str.rjust(longitud)[:longitud]
    else:
        return valor_str.ljust(longitud)[:longitud]


def formatear_importe(valor: float, decimales: int = 2) -> str:
    """Formatea un importe con coma como separador decimal"""
    try:
        if valor is None:
            valor = 0.0
        valor_float = float(valor)
        # Formatear con coma como separador decimal
        formato = f"{{:.{decimales}f}}".format(valor_float)
        return formato.replace(".", ",")
    except:
        return "0,00"


def generar_registro_mmb(factura_data: Dict, config: Optional[Dict] = None) -> str:
    """
    Genera un registro en formato .mmb para una factura
    
    Estructura del registro (basada en el análisis):
    - Pos 0-0: Tipo registro (V)
    - Pos 2-11: Fecha 1 (DD/MM/YYYY)
    - Pos 12-21: Fecha 2 (DD/MM/YYYY)
    - Pos 32-36: Número factura (5 dígitos)
    - Pos 44-54: Código cliente (11 dígitos)
    - Pos 60-68: NIF/CIF (9 caracteres)
    - Pos 74-93: Nombre cliente (20 caracteres)
    - Pos 104-123: Descripción (20 caracteres)
    - Pos 143-149: Base imponible (7 caracteres con formato XXXX,XX)
    - Pos 158-162: IVA % (5 caracteres con formato XX,XX)
    - Pos 163-169: IVA € (7 caracteres con formato XXXX,XX)
    - Pos 178-188: Código contable 1 (11 dígitos)
    - Pos 266-272: Total (7 caracteres con formato XXXX,XX)
    - Pos 282-292: Código contable 2 (11 dígitos)
    - Pos 292+: Código contable 3 y otros campos
    """
    if config is None:
        config = {}
    
    # Valores por defecto
    tipo_registro = "V"
    
    # Obtener fecha de emisión con manejo robusto
    fecha_emision_raw = factura_data.get('fecha_emision') or factura_data.get('fecha_envio')
    
    # Función auxiliar para normalizar fechas
    def normalizar_fecha(fecha_input) -> str:
        """Normaliza una fecha a formato DD/MM/YYYY con validación robusta"""
        if not fecha_input:
            return datetime.now().strftime("%d/%m/%Y")
        
        # Convertir a string si no lo es
        fecha_str = str(fecha_input).strip()
        if not fecha_str or fecha_str.lower() in ('none', 'null', 'nan'):
            return datetime.now().strftime("%d/%m/%Y")
        
        # Si ya está en formato DD/MM/YYYY, validar y retornar
        if "/" in fecha_str and len(fecha_str) >= 10:
            try:
                # Intentar parsear como DD/MM/YYYY
                partes = fecha_str.split("/")
                if len(partes) == 3:
                    dia, mes, anio = partes[0], partes[1], partes[2]
                    # Validar rango de años razonable (1900-2100)
                    anio_int = int(anio)
                    if 1900 <= anio_int <= 2100:
                        fecha_obj = datetime.strptime(f"{dia.zfill(2)}/{mes.zfill(2)}/{anio}", "%d/%m/%Y")
                        return fecha_obj.strftime("%d/%m/%Y")
            except (ValueError, TypeError, IndexError):
                pass
        
        # Si viene en formato YYYY-MM-DD
        if "-" in fecha_str and len(fecha_str) >= 10:
            try:
                fecha_partes = fecha_str[:10].split("-")
                if len(fecha_partes) == 3:
                    anio, mes, dia = fecha_partes[0], fecha_partes[1], fecha_partes[2]
                    anio_int = int(anio)
                    # Validar rango de años razonable (1900-2100)
                    if 1900 <= anio_int <= 2100:
                        fecha_obj = datetime.strptime(f"{anio}-{mes}-{dia}", "%Y-%m-%d")
                        return fecha_obj.strftime("%d/%m/%Y")
            except (ValueError, TypeError, IndexError, OverflowError):
                pass
        
        # Si es un timestamp numérico (Unix timestamp)
        try:
            timestamp = float(fecha_str)
            # Validar que sea un timestamp razonable (entre 1970 y 2100)
            if 0 <= timestamp <= 4102444800:  # 2100-01-01 en timestamp
                fecha_obj = datetime.fromtimestamp(timestamp)
                return fecha_obj.strftime("%d/%m/%Y")
        except (ValueError, TypeError, OSError, OverflowError):
            pass
        
        # Si todo falla, usar fecha actual
        logger.warning(f"No se pudo parsear la fecha '{fecha_input}', usando fecha actual")
        return datetime.now().strftime("%d/%m/%Y")
    
    fecha_emision = normalizar_fecha(fecha_emision_raw)
    
    num_factura_raw = str(factura_data.get('num_factura', '')).strip()
    # Extraer solo los dígitos del número de factura
    num_factura_digitos = re.sub(r'[^0-9]', '', num_factura_raw)
    num_factura = num_factura_digitos[:5] if num_factura_digitos else num_factura_raw[:5]
    
    # Nombre del cliente: debe ir en MAYÚSCULAS y completo (aunque se limite a 20 caracteres para el campo)
    cliente_nombre_raw = factura_data.get('cliente_nombre', factura_data.get('cliente', '')).strip()
    cliente_nombre_upper = cliente_nombre_raw.upper()  # Nombre completo en mayúsculas para usar en descripción
    cliente_nombre = cliente_nombre_upper[:20]  # Limitar a 20 caracteres solo para el campo nombre
    cliente_nif = factura_data.get('cliente_nif', '').strip()[:9]
    
    # Detectar si es factura intracomunitaria (exenta de IVA)
    # Las facturas intracomunitarias empiezan con "A" o "A25"
    num_factura_upper = num_factura_raw.upper()
    serie_factura = factura_data.get('serie_factura', '').upper()
    es_intracomunitaria = (
        num_factura_upper.startswith('A') or 
        num_factura_upper.startswith('A25') or
        serie_factura.startswith('A25') or
        serie_factura.startswith('A')
    )
    
    # Obtener códigos
    # Código de cliente (430...) - viene de la hoja CLIENTES o se genera
    codigo_cliente = factura_data.get('codigo_cliente', obtener_codigo_cliente_contable(cliente_nif))
    
    # Importes - intentar obtener desde múltiples fuentes
    # Prioridad: base_imponible del XML > importe de BD > 0
    base_imponible_raw = factura_data.get('base_imponible') or factura_data.get('importe') or 0.0
    base_imponible = float(base_imponible_raw) if base_imponible_raw else 0.0
    
    # IVA porcentaje - del XML o por defecto 21%
    iva_porcentaje_raw = factura_data.get('iva_porcentaje') or 21.0
    iva_porcentaje = float(iva_porcentaje_raw) if iva_porcentaje_raw else 21.0
    
    # IVA importe - del XML o calcular desde base
    iva_importe_raw = factura_data.get('iva_importe')
    if iva_importe_raw is not None and float(iva_importe_raw) > 0:
        # Si tenemos IVA del XML y es mayor que 0, usarlo
        iva_importe = float(iva_importe_raw)
        logger.debug(f"IVA importe desde XML: {iva_importe}")
    else:
        # Calcular desde base e IVA porcentaje si no tenemos IVA o es 0
        if base_imponible > 0 and iva_porcentaje > 0:
            iva_importe = base_imponible * iva_porcentaje / 100.0
            logger.debug(f"IVA importe calculado desde base ({base_imponible}) e IVA% ({iva_porcentaje}): {iva_importe}")
        else:
            iva_importe = 0.0
            logger.warning(f"No se pudo calcular IVA: base={base_imponible}, IVA%={iva_porcentaje}")
    
    # Total - del XML o calcular desde base + IVA
    total_raw = factura_data.get('total') or factura_data.get('importe')
    if total_raw is not None:
        total = float(total_raw) if total_raw else 0.0
    else:
        # Calcular desde base + IVA
        total = base_imponible + iva_importe
    
    # Si es intracomunitaria, el IVA debe ser 0
    if es_intracomunitaria:
        iva_porcentaje = 0.0
        iva_importe = 0.0
        # Si tenemos total, la base es el total
        if total > 0:
            base_imponible = total
        # Si no tenemos total pero tenemos base, el total es la base
        elif base_imponible > 0:
            total = base_imponible
    
    # Si solo tenemos el importe total (de la BD), calcular base e IVA
    if base_imponible == 0.0 and total > 0:
        if es_intracomunitaria:
            base_imponible = total
            iva_importe = 0.0
        else:
            # Calcular base desde total con IVA
            base_imponible = total / (1 + iva_porcentaje / 100.0)
            iva_importe = total - base_imponible
    
    # Validar que al menos tengamos algún importe
    if base_imponible == 0.0 and total == 0.0:
        logger.warning(f"Factura {num_factura} tiene todos los importes en 0. Datos: {factura_data}")
        # Intentar usar el importe de la BD como último recurso
        importe_bd = factura_data.get('importe', 0.0)
        if importe_bd and float(importe_bd) > 0:
            total = float(importe_bd)
            if es_intracomunitaria:
                base_imponible = total
                iva_importe = 0.0
            else:
                base_imponible = total / (1 + iva_porcentaje / 100.0)
                iva_importe = total - base_imponible
    
    # Verificación final: si tenemos base y porcentaje pero IVA es 0, recalcular
    if base_imponible > 0 and iva_porcentaje > 0 and iva_importe == 0.0 and not es_intracomunitaria:
        iva_importe = base_imponible * iva_porcentaje / 100.0
        logger.info(f"IVA recalculado antes de generar registro: base={base_imponible}, IVA%={iva_porcentaje}, IVA={iva_importe}")
    
    # Asegurar que el total sea siempre base + IVA (excepto intracomunitarias)
    if not es_intracomunitaria and base_imponible > 0:
        total_calculado = base_imponible + iva_importe
        if abs(total - total_calculado) > 0.01:  # Si hay diferencia significativa, usar el calculado
            logger.info(f"Total corregido: {total} -> {total_calculado} (base + IVA)")
            total = total_calculado
    elif es_intracomunitaria:
        # Para intracomunitarias, el total es igual a la base
        total = base_imponible
    
    # Código contable del IVA (477...) - solo si NO es intracomunitaria
    if es_intracomunitaria:
        # Intracomunitaria: no hay cuenta 477, solo 430 y 705
        codigo_contable_1 = ""  # Vacío para intracomunitarias
    else:
        # Código contable del IVA según el porcentaje
        # 47700000021 para IVA al 21%, 47700000010 para IVA al 10%
        if abs(iva_porcentaje - 21.0) < 0.1:  # IVA al 21%
            codigo_contable_1 = '47700000021'
        elif abs(iva_porcentaje - 10.0) < 0.1:  # IVA al 10%
            codigo_contable_1 = '47700000010'
        else:
            # Por defecto usar 21% si no coincide con ninguno
            codigo_contable_1 = factura_data.get('codigo_contable_1', '47700000021')
    
    # Código contable de ventas (705...) - siempre fijo
    codigo_contable_2 = '70500000000'
    
    # Logging final antes de generar registro
    logger.info(f"Generando registro MMB - Factura {num_factura}: base={base_imponible}, IVA%={iva_porcentaje}, IVA_importe={iva_importe}, total={total}, cliente={cliente_nombre}")
    
    # Descripción: debe incluir "NTRA. FRA. N " + número factura + parte del nombre del cliente
    # Ejemplo: "NTRA. FRA. N 25405 C2C INVER PARK, S" (20 caracteres)
    # Usar solo los dígitos del número de factura (máximo 5) para dejar más espacio al nombre
    num_factura_para_desc = num_factura[:5]  # Solo 5 dígitos para dejar más espacio
    # Usar "N " en lugar de "N°" para coincidir con la plantilla
    prefijo_desc = f"NTRA. FRA. N {num_factura_para_desc}"
    espacio_restante = 20 - len(prefijo_desc)
    if espacio_restante > 0:
        # Añadir parte del nombre del cliente completo (en mayúsculas) hasta completar 20 caracteres
        # Si hay espacio, añadir un espacio y luego el nombre del cliente
        nombre_para_desc = cliente_nombre_upper[:espacio_restante-1] if espacio_restante > 1 else ""
        if nombre_para_desc:
            descripcion = (prefijo_desc + " " + nombre_para_desc)[:20].ljust(20)
        else:
            descripcion = prefijo_desc[:20].ljust(20)
    else:
        descripcion = prefijo_desc[:20].ljust(20)
    
    # Construir registro
    registro = ""
    registro += tipo_registro  # Pos 0
    registro += " "  # Pos 1
    registro += fecha_emision.ljust(10)  # Pos 2-11: Fecha 1
    registro += fecha_emision.ljust(10)  # Pos 12-21: Fecha 2
    registro += " " * 10  # Pos 22-31
    registro += num_factura[:5].rjust(5)  # Pos 32-36: Número factura
    registro += " " * 7  # Pos 37-43
    registro += codigo_cliente[:11].ljust(11)  # Pos 44-54: Código cliente
    registro += " " * 5  # Pos 55-59
    registro += cliente_nif[:9].ljust(9)  # Pos 60-68: NIF/CIF
    registro += " " * 5  # Pos 69-73
    registro += cliente_nombre[:20].ljust(20)  # Pos 74-93: Nombre cliente
    registro += " " * 10  # Pos 94-103
    registro += descripcion[:20].ljust(20)  # Pos 104-123: Descripción
    registro += " " * 19  # Pos 124-142
    # Base imponible (pos 143-149): 7 caracteres con espacio al inicio para alineación
    base_str = formatear_importe(base_imponible, 2).replace(" ", "")
    registro += (" " + base_str).rjust(7)[:7]  # Pos 143-149: Base imponible (espacio + valor)
    registro += " " * 8  # Pos 150-157
    # IVA: porcentaje e importe concatenados (pos 158-169 = 12 caracteres)
    # Formato: " 21,001104,4" (1 espacio + 5 caracteres IVA% + 6 caracteres IVA€ = 12 caracteres totales)
    # El importe de IVA debe tener formato XXXX,X (4 dígitos + coma + 1 decimal = 6 caracteres)
    # El espacio va al inicio del campo completo, NO entre porcentaje e importe
    iva_porcentaje_str = formatear_importe(iva_porcentaje, 2).replace(" ", "").rjust(5)[:5]  # Pos 159-163: IVA % (5 caracteres)
    # Formatear importe de IVA con 1 decimal (no 2) para coincidir con la plantilla
    iva_importe_float = float(iva_importe)
    iva_importe_str = f"{iva_importe_float:.1f}".replace(".", ",")  # Formato con 1 decimal
    # Asegurar que tenga 4 dígitos antes de la coma (rellenar con espacios a la izquierda si es necesario)
    partes = iva_importe_str.split(",")
    if len(partes) == 2:
        digitos_antes = len(partes[0])
        if digitos_antes < 4:
            # Rellenar con espacios a la izquierda hasta tener 4 dígitos antes de la coma
            espacios_necesarios = 4 - digitos_antes
            iva_importe_str = " " * espacios_necesarios + iva_importe_str
    # Asegurar exactamente 6 caracteres para el campo IVA (formato: XXXX,X)
    iva_importe_str = iva_importe_str[:6].rjust(6)
    # Campo IVA completo: espacio al inicio + porcentaje + importe (12 caracteres totales)
    # El espacio va al inicio, NO entre porcentaje e importe
    iva_completo = " " + iva_porcentaje_str + iva_importe_str  # 1 + 5 + 6 = 12 caracteres
    registro += iva_completo[:12].ljust(12)  # Pos 158-169: IVA completo (12 caracteres)
    registro += " " * 8  # Pos 170-177
    # Código contable 1 (477 para IVA) - solo si NO es intracomunitaria
    if codigo_contable_1:
        registro += codigo_contable_1[:11].ljust(11)  # Pos 178-188: Código contable 1 (IVA)
    else:
        registro += " " * 11  # Vacío para intracomunitarias
    registro += " " * 77  # Pos 189-265
    # Total (pos 266-272): 7 caracteres con espacio al inicio para alineación
    total_str = formatear_importe(total, 2).replace(" ", "")
    registro += (" " + total_str).rjust(7)[:7]  # Pos 266-272: Total (espacio + valor)
    registro += " " * 9  # Pos 273-281
    registro += codigo_contable_2[:11].ljust(11)  # Pos 282-292: Código contable 2 (705 - Ventas)
    registro += " " * 7  # Pos 293-299
    # Importe de base imponible para la cuenta 705 (pos 300-306): 7 caracteres
    # Según la plantilla, este campo puede tener un formato diferente
    base_705_str = formatear_importe(base_imponible, 2).replace(" ", "")
    registro += base_705_str[:7].ljust(7)  # Pos 300-306: Base imponible para 705
    registro += " " * 113  # Pos 307-419: Espacios hasta antes de Criterio de Caja
    # Criterio de Caja (pos 420): El sistema requiere "N" o "S", aunque la plantilla tenga espacios
    # "N" = No aplica criterio de caja, "S" = Sí aplica criterio de caja
    registro += "N"  # Pos 420: Criterio de Caja (N = No aplica)
    registro += " " * 46  # Pos 421-466: Espacios adicionales
    registro += "N"  # Pos 467: Flag (N)
    registro += " "  # Pos 468: Espacio final (total 468 caracteres)
    
    # Asegurar longitud exacta de 468 caracteres (como el archivo plantilla)
    # IMPORTANTE: Truncar a 468 y rellenar con espacios si es necesario
    registro = registro[:468].ljust(468)
    
    # Verificación final: asegurar que la posición 467 tenga "N" (flag final)
    # y que el registro tenga exactamente 468 caracteres
    if len(registro) >= 468:
        # Asegurar "N" en posición 467 (índice 467) y mantener 468 caracteres
        registro = registro[:467] + "N" + (registro[468:] if len(registro) > 468 else "")
    else:
        # Rellenar hasta pos 467, añadir "N" y asegurar 468 caracteres
        registro = (registro.ljust(467) + "N").ljust(468)
    
    return registro


def obtener_cuenta_contable_desde_excel(excel_path: str, empresa_nombre: str) -> Optional[str]:
    """
    Obtiene el código de cliente contable (430...) de una empresa desde la hoja CLIENTES del Excel.
    
    Args:
        excel_path: Ruta del archivo Excel
        empresa_nombre: Nombre de la empresa (normalizado, sin tildes)
    
    Returns:
        Código de cliente contable (430...) o None si no se encuentra
    """
    if not excel_path or not os.path.exists(excel_path):
        return None
    
    try:
        # Leer hoja CLIENTES
        df_clientes = macro_adapter._read_clientes_df_from_same_book(excel_path)
        if df_clientes.empty:
            return None
        
        # Buscar columnas posibles para cuenta contable (código de cliente 430...)
        # También buscar variantes con espacios, guiones, etc.
        posibles_columnas = [
            'cuenta_contable', 'codigo_contable', 'cuenta contable', 
            'codigo contable', 'cuenta', 'codigo', 'cta_contable',
            'codigo_cliente', 'codigo cliente', 'cuenta_cliente', 'cuenta cliente',
            '430', 'codigo_430', 'codigo 430'
        ]
        
        columna_cuenta = None
        for col in posibles_columnas:
            if col in df_clientes.columns:
                columna_cuenta = col
                break
        
        if not columna_cuenta:
            logger.debug("No se encontró columna de cuenta contable en hoja CLIENTES")
            return None
        
        # Normalizar nombre de empresa para búsqueda (sin tildes)
        empresa_norm = prueba.quitar_tildes_empresa(empresa_nombre).lower().strip()
        logger.debug(f"Buscando cuenta contable para empresa: '{empresa_nombre}' (normalizado: '{empresa_norm}')")
        
        # Buscar por nombre de empresa (búsqueda exacta primero)
        if 'empresa_nombre' in df_clientes.columns:
            for idx, row in df_clientes.iterrows():
                nombre_emp_raw = str(row.get('empresa_nombre', '')).strip()
                if not nombre_emp_raw or nombre_emp_raw.lower() in ('nan', 'none', ''):
                    continue
                nombre_emp = prueba.quitar_tildes_empresa(nombre_emp_raw).lower().strip()
                
                # Búsqueda exacta
                if nombre_emp == empresa_norm:
                    cuenta_raw = row.get(columna_cuenta, '')
                    # Convertir a string y limpiar (puede venir como float 43000000236.0)
                    if cuenta_raw is not None:
                        cuenta = str(cuenta_raw).strip()
                        # Si es un float, quitar el .0
                        if cuenta.endswith('.0'):
                            cuenta = cuenta[:-2]
                        if cuenta and cuenta.lower() not in ('nan', 'none', ''):
                            logger.info(f"Cuenta contable encontrada (exacta) para '{empresa_nombre}': {cuenta}")
                            return cuenta
                
                # Búsqueda parcial (si contiene el nombre normalizado)
                if empresa_norm in nombre_emp or nombre_emp in empresa_norm:
                    cuenta_raw = row.get(columna_cuenta, '')
                    # Convertir a string y limpiar (puede venir como float 43000000236.0)
                    if cuenta_raw is not None:
                        cuenta = str(cuenta_raw).strip()
                        # Si es un float, quitar el .0
                        if cuenta.endswith('.0'):
                            cuenta = cuenta[:-2]
                        if cuenta and cuenta.lower() not in ('nan', 'none', ''):
                            logger.info(f"Cuenta contable encontrada (parcial) para '{empresa_nombre}': {cuenta}")
                            return cuenta
        
        # Si no se encuentra, intentar con nombre_legal
        if 'nombre_legal' in df_clientes.columns:
            for idx, row in df_clientes.iterrows():
                nombre_emp_raw = str(row.get('nombre_legal', '')).strip()
                if not nombre_emp_raw or nombre_emp_raw.lower() in ('nan', 'none', ''):
                    continue
                nombre_emp = prueba.quitar_tildes_empresa(nombre_emp_raw).lower().strip()
                
                # Búsqueda exacta
                if nombre_emp == empresa_norm:
                    cuenta = str(row.get(columna_cuenta, '')).strip()
                    if cuenta and cuenta.lower() not in ('nan', 'none', ''):
                        logger.info(f"Cuenta contable encontrada (nombre_legal exacta) para '{empresa_nombre}': {cuenta}")
                        return cuenta
                
                # Búsqueda parcial
                if empresa_norm in nombre_emp or nombre_emp in empresa_norm:
                    cuenta = str(row.get(columna_cuenta, '')).strip()
                    if cuenta and cuenta.lower() not in ('nan', 'none', ''):
                        logger.info(f"Cuenta contable encontrada (nombre_legal parcial) para '{empresa_nombre}': {cuenta}")
                        return cuenta
        
        logger.warning(f"No se encontró cuenta contable para empresa '{empresa_nombre}' en Excel {excel_path}")
        return None
    except Exception as e:
        logger.warning(f"Error leyendo cuenta contable desde Excel {excel_path}: {e}")
        return None


def generar_archivo_mmb(
    fecha_desde: Optional[str] = None,
    fecha_hasta: Optional[str] = None,
    empresa: Optional[str] = None,
    ruta_salida: Optional[str] = None,
    logs_dir: str = "logs",
    responses_dir: str = "responses",
    excel_path: Optional[str] = None,
    facturas_ids: Optional[List[int]] = None,
    config: Optional[Dict] = None
) -> str:
    """
    Genera un archivo .mmb con las facturas emitidas
    
    Args:
        fecha_desde: Fecha desde (formato YYYY-MM-DD)
        fecha_hasta: Fecha hasta (formato YYYY-MM-DD)
        empresa: Filtrar por empresa (None = todas)
        ruta_salida: Ruta donde guardar el archivo .mmb
        logs_dir: Directorio donde están los XMLs de logs
        responses_dir: Directorio donde están los XMLs de responses
        excel_path: Ruta del Excel para leer cuenta contable (si no se proporciona, se busca en la BD)
        facturas_ids: Lista de IDs de facturas específicas a exportar (tiene prioridad sobre filtros)
        config: Configuración adicional (códigos contables, etc.)
    
    Returns:
        Ruta del archivo generado
    """
    # Construir consulta SQL (incluir excel_path si existe)
    query = """
        SELECT fecha_envio, num_factura, empresa, estado, detalles, 
               pdf_url, importe, cliente, excel_path
        FROM envios
        WHERE 1=1
    """
    params = []
    
    # Si se proporcionan IDs específicos, usar esos (tiene prioridad)
    if facturas_ids:
        placeholders = ','.join(['?'] * len(facturas_ids))
        query += f" AND id IN ({placeholders})"
        params.extend(facturas_ids)
    else:
        # Usar filtros de fecha y empresa
        if fecha_desde:
            query += " AND substr(fecha_envio, 1, 10) >= ?"
            params.append(fecha_desde)
        
        if fecha_hasta:
            query += " AND substr(fecha_envio, 1, 10) <= ?"
            params.append(fecha_hasta)
        
        if empresa:
            query += " AND empresa = ?"
            params.append(empresa)
    
    # Solo facturas exitosas
    query += " AND estado IN ('ÉXITO', 'DUPLICADO')"
    query += " ORDER BY fecha_envio, num_factura"
    
    # Obtener facturas de la base de datos
    facturas = fetch_all(query, params)
    
    if not facturas:
        raise ValueError("No se encontraron facturas para exportar")
    
    logger.info(f"Generando archivo .mmb con {len(facturas)} facturas")
    
    # Preparar datos de facturas
    registros_mmb = []
    
    # Cache para cuentas contables por empresa
    cuentas_contables_cache = {}
    
    # Determinar ruta del Excel a usar
    excel_path_a_usar = excel_path
    if not excel_path_a_usar and facturas:
        # Intentar obtener desde la primera factura
        primera_factura = facturas[0]
        if len(primera_factura) > 8:
            excel_path_a_usar = primera_factura[8]  # excel_path está en la posición 8
    
    for row in facturas:
        # Manejar tanto con como sin excel_path
        if len(row) >= 9:
            fecha_envio, num_factura, empresa_db, estado, detalles, pdf_url, importe, cliente, excel_path_row = row
        else:
            fecha_envio, num_factura, empresa_db, estado, detalles, pdf_url, importe, cliente = row
            excel_path_row = None
        
        # Datos base desde la BD
        factura_data = {
            'fecha_envio': fecha_envio,
            'num_factura': num_factura,
            'empresa': empresa_db,
            'cliente': cliente,
            'importe': importe or 0.0,
        }
        
        # Intentar obtener código de cliente (430...) desde Excel
        # IMPORTANTE: Buscar por el nombre del CLIENTE, no por el nombre de la empresa emisora
        # El código de cliente está asociado al cliente receptor en la hoja CLIENTES
        cliente_nombre_bd = cliente  # Nombre del cliente desde la BD
        if cliente_nombre_bd:
            # Crear clave única para el cache: cliente + excel_path
            excel_para_buscar = excel_path_a_usar or excel_path_row
            cache_key = f"{cliente_nombre_bd}|{excel_para_buscar}" if excel_para_buscar else cliente_nombre_bd
            
            if cache_key not in cuentas_contables_cache:
                if excel_para_buscar and os.path.exists(excel_para_buscar):
                    logger.info(f"Buscando código de cliente para CLIENTE '{cliente_nombre_bd}' en Excel: {excel_para_buscar}")
                    codigo_cliente = obtener_cuenta_contable_desde_excel(excel_para_buscar, cliente_nombre_bd)
                    if codigo_cliente:
                        cuentas_contables_cache[cache_key] = codigo_cliente
                        logger.info(f"✓ Código de cliente encontrado para CLIENTE '{cliente_nombre_bd}': {codigo_cliente}")
                    else:
                        logger.warning(f"✗ No se encontró código de cliente para CLIENTE '{cliente_nombre_bd}' en Excel {excel_para_buscar}. Se generará uno automático.")
            
            # Añadir código de cliente al factura_data si está disponible
            if cache_key in cuentas_contables_cache:
                factura_data['codigo_cliente'] = cuentas_contables_cache[cache_key]
                logger.info(f"Código de cliente asignado a factura {num_factura} (cliente: {cliente_nombre_bd}): {cuentas_contables_cache[cache_key]}")
            else:
                logger.warning(f"Factura {num_factura}: No se encontró código de cliente para CLIENTE '{cliente_nombre_bd}'. Se generará uno automático basado en el NIF.")
        else:
            logger.warning(f"Factura {num_factura}: No hay nombre de cliente en la BD. Se generará código automático basado en el NIF.")
        
        # Intentar obtener datos adicionales desde XML
        xml_path = buscar_xml_factura(num_factura, empresa_db, logs_dir, responses_dir)
        if xml_path:
            datos_xml = obtener_datos_factura_desde_xml(xml_path)
            if datos_xml:
                # Si el importe de la BD es 0 pero tenemos datos del XML, usar los del XML
                if (not factura_data.get('importe') or float(factura_data.get('importe', 0) or 0) == 0):
                    if datos_xml.get('total'):
                        factura_data['importe'] = datos_xml['total']
                    if datos_xml.get('base_imponible'):
                        factura_data['base_imponible'] = datos_xml['base_imponible']
                    if datos_xml.get('iva_importe'):
                        factura_data['iva_importe'] = datos_xml['iva_importe']
                factura_data.update(datos_xml)
                logger.debug(f"Factura {num_factura}: Datos del XML - base: {datos_xml.get('base_imponible')}, IVA: {datos_xml.get('iva_importe')}, total: {datos_xml.get('total')}")
                
                # Si no encontramos el código de cliente antes y ahora tenemos el nombre del cliente del XML, intentar buscarlo
                if not factura_data.get('codigo_cliente') and datos_xml.get('cliente_nombre'):
                    cliente_xml = datos_xml.get('cliente_nombre')
                    if excel_para_buscar and os.path.exists(excel_para_buscar):
                        cache_key_xml = f"{cliente_xml}|{excel_para_buscar}"
                        if cache_key_xml not in cuentas_contables_cache:
                            logger.info(f"Buscando código de cliente para CLIENTE '{cliente_xml}' (desde XML) en Excel: {excel_para_buscar}")
                            codigo_cliente = obtener_cuenta_contable_desde_excel(excel_para_buscar, cliente_xml)
                            if codigo_cliente:
                                cuentas_contables_cache[cache_key_xml] = codigo_cliente
                                factura_data['codigo_cliente'] = codigo_cliente
                                logger.info(f"✓ Código de cliente encontrado para CLIENTE '{cliente_xml}' (desde XML): {codigo_cliente}")
        else:
            logger.warning(f"No se encontró XML para factura {num_factura} de {empresa_db}")
        
        # Si no hay fecha de emisión, usar fecha_envio
        if 'fecha_emision' not in factura_data:
            factura_data['fecha_emision'] = fecha_envio
        
        # Logging para diagnóstico
        logger.info(f"Factura {num_factura}: Datos finales - importe BD: {importe}, base: {factura_data.get('base_imponible')}, IVA_importe: {factura_data.get('iva_importe')}, IVA_%: {factura_data.get('iva_porcentaje')}, total: {factura_data.get('total')}, codigo_cliente: {factura_data.get('codigo_cliente', 'NO ENCONTRADO')}, cliente: {factura_data.get('cliente_nombre', factura_data.get('cliente', 'N/A'))}")
        
        # Generar registro (el código de cliente ya está en factura_data si se encontró)
        registro = generar_registro_mmb(factura_data, config)
        registros_mmb.append(registro)
    
    # Generar nombre de archivo si no se proporciona
    if not ruta_salida:
        fecha_actual = datetime.now().strftime("%Y%m%d")
        ruta_salida = f"Facturas_Emitidas_{fecha_actual}.mmb"
    
    # Escribir archivo
    with open(ruta_salida, 'w', encoding='utf-8', errors='replace') as f:
        # Escribir todos los registros en una sola línea (formato del archivo original)
        contenido = "".join(registros_mmb)
        f.write(contenido)
    
    logger.info(f"Archivo .mmb generado: {ruta_salida}")
    return ruta_salida

