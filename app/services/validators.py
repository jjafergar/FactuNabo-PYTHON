# -*- coding: utf-8 -*-
"""
Módulo de validación de documentos de identificación españoles.
Implementa los algoritmos oficiales de validación de NIF, CIF y NIE.
"""
import re
from typing import Tuple, Optional


def validate_nif(nif: str) -> Tuple[bool, Optional[str]]:
    """
    Valida un NIF (Número de Identificación Fiscal) español.
    
    Formato: 8 dígitos + 1 letra de control
    Ejemplo: 12345678Z
    
    Args:
        nif: NIF a validar (puede contener espacios, guiones, etc.)
    
    Returns:
        Tuple[bool, Optional[str]]: (es_válido, mensaje_error)
    """
    if not nif:
        return False, "NIF vacío"
    
    # Limpiar el NIF
    nif_clean = re.sub(r'[\s\-\._]', '', str(nif).strip().upper())
    
    # Verificar formato básico
    if not re.match(r'^\d{8}[A-Z]$', nif_clean):
        return False, f"Formato inválido. Debe ser 8 dígitos + 1 letra (ej: 12345678Z)"
    
    # Extraer número y letra
    numero = nif_clean[:8]
    letra = nif_clean[8]
    
    # Calcular letra de control
    letras_control = "TRWAGMYFPDXBNJZSQVHLCKE"
    resto = int(numero) % 23
    letra_correcta = letras_control[resto]
    
    if letra != letra_correcta:
        return False, f"Dígito de control incorrecto. Debería ser '{letra_correcta}' en lugar de '{letra}'"
    
    return True, None


def validate_cif(cif: str) -> Tuple[bool, Optional[str]]:
    """
    Valida un CIF (Código de Identificación Fiscal) español.
    
    Formato: 1 letra + 7 dígitos + 1 carácter de control (dígito o letra)
    Ejemplo: B12345674, A12345675, Q1234567I
    
    Args:
        cif: CIF a validar (puede contener espacios, guiones, etc.)
    
    Returns:
        Tuple[bool, Optional[str]]: (es_válido, mensaje_error)
    """
    if not cif:
        return False, "CIF vacío"
    
    # Limpiar el CIF
    cif_clean = re.sub(r'[\s\-\._]', '', str(cif).strip().upper())
    
    # Verificar formato básico
    if not re.match(r'^[ABCDEFGHJNPQRSUVW]\d{7}[0-9A-J]$', cif_clean):
        return False, f"Formato inválido. Debe ser 1 letra + 7 dígitos + 1 carácter de control"
    
    # Extraer partes
    letra_inicial = cif_clean[0]
    numero = cif_clean[1:8]
    digito_control = cif_clean[8]
    
    # Calcular dígito de control
    suma_pares = sum(int(numero[i]) for i in range(1, 7, 2))
    suma_impares = sum(int(numero[i]) for i in range(0, 7, 2))
    
    # Multiplicar impares por 2 y sumar dígitos
    suma_impares_doble = 0
    for i in range(0, 7, 2):
        doble = int(numero[i]) * 2
        suma_impares_doble += (doble // 10) + (doble % 10)
    
    suma_total = suma_pares + suma_impares_doble
    unidad = suma_total % 10
    digito_calculado = (10 - unidad) % 10
    
    # Para letras iniciales que usan letra de control
    letras_control = "JABCDEFGHI"
    
    # Determinar tipo de control según letra inicial
    if letra_inicial in ['P', 'Q', 'R', 'S', 'W']:
        # Usa letra de control
        letra_correcta = letras_control[digito_calculado]
        if digito_control != letra_correcta:
            return False, f"Dígito de control incorrecto. Debería ser '{letra_correcta}' en lugar de '{digito_control}'"
    elif letra_inicial in ['K', 'L', 'M']:
        # Usa letra de control (empresas extranjeras)
        letra_correcta = letras_control[digito_calculado]
        if digito_control != letra_correcta:
            return False, f"Dígito de control incorrecto. Debería ser '{letra_correcta}' en lugar de '{digito_control}'"
    else:
        # Usa dígito de control
        if digito_control != str(digito_calculado):
            return False, f"Dígito de control incorrecto. Debería ser '{digito_calculado}' en lugar de '{digito_control}'"
    
    return True, None


def validate_nie(nie: str) -> Tuple[bool, Optional[str]]:
    """
    Valida un NIE (Número de Identidad de Extranjero) español.
    
    Formato: 1 letra (X, Y, Z) + 7 dígitos + 1 letra de control
    Ejemplo: X1234567L, Y7654321M
    
    Args:
        nie: NIE a validar (puede contener espacios, guiones, etc.)
    
    Returns:
        Tuple[bool, Optional[str]]: (es_válido, mensaje_error)
    """
    if not nie:
        return False, "NIE vacío"
    
    # Limpiar el NIE
    nie_clean = re.sub(r'[\s\-\._]', '', str(nie).strip().upper())
    
    # Verificar formato básico
    if not re.match(r'^[XYZ]\d{7}[A-Z]$', nie_clean):
        return False, f"Formato inválido. Debe ser X/Y/Z + 7 dígitos + 1 letra (ej: X1234567L)"
    
    # Extraer partes
    letra_inicial = nie_clean[0]
    numero = nie_clean[1:8]
    letra_control = nie_clean[8]
    
    # Reemplazar letra inicial por número
    reemplazo = {'X': '0', 'Y': '1', 'Z': '2'}
    numero_completo = reemplazo[letra_inicial] + numero
    
    # Calcular letra de control (igual que NIF)
    letras_control = "TRWAGMYFPDXBNJZSQVHLCKE"
    resto = int(numero_completo) % 23
    letra_correcta = letras_control[resto]
    
    if letra_control != letra_correcta:
        return False, f"Dígito de control incorrecto. Debería ser '{letra_correcta}' en lugar de '{letra_control}'"
    
    return True, None


def validate_nif_iva(nif_iva: str) -> Tuple[bool, Optional[str]]:
    """
    Valida un NIF-IVA para facturas intracomunitarias.
    
    Formato: Código país (2 letras) + NIF del país (sin espacios)
    Ejemplo: ES12345678Z (España), FR25533970034 (Francia), DE123456789 (Alemania)
    
    Args:
        nif_iva: NIF-IVA a validar
    
    Returns:
        Tuple[bool, Optional[str]]: (es_válido, mensaje_error)
    """
    if not nif_iva:
        return False, "NIF-IVA vacío"
    
    nif_iva_clean = re.sub(r'[\s\-\._]', '', str(nif_iva).strip().upper())
    
    # Códigos de país válidos de la UE
    codigos_pais_ue = {
        'AT', 'BE', 'BG', 'CY', 'CZ', 'DE', 'DK', 'EE', 'ES', 'FI', 
        'FR', 'GR', 'HR', 'HU', 'IE', 'IT', 'LT', 'LU', 'LV', 'MT', 
        'NL', 'PL', 'PT', 'RO', 'SE', 'SI', 'SK'
    }
    
    # Debe tener al menos 2 caracteres (código de país)
    if len(nif_iva_clean) < 2:
        return False, "NIF-IVA debe tener al menos un código de país de 2 letras"
    
    # Extraer código de país
    codigo_pais = nif_iva_clean[:2]
    
    # Verificar que el código de país sea válido
    if codigo_pais not in codigos_pais_ue:
        return False, f"Código de país '{codigo_pais}' no válido. Debe ser un código de país de la UE (ej: ES, FR, DE, IT, etc.)"
    
    # Extraer el documento sin el prefijo del país
    documento = nif_iva_clean[2:]
    
    # Si no hay documento después del código de país
    if not documento:
        return False, f"NIF-IVA debe incluir el número de identificación después del código de país '{codigo_pais}'"
    
    # Si el código de país es ES (España), validar con algoritmos españoles
    if codigo_pais == 'ES':
        # Validar según el tipo de documento español
        if re.match(r'^\d{8}[A-Z]$', documento):
            # Es un NIF
            valido, error = validate_nif(documento)
            if not valido:
                return False, f"NIF-IVA inválido: {error}"
        elif re.match(r'^[ABCDEFGHJNPQRSUVW]\d{7}[0-9A-J]$', documento):
            # Es un CIF
            valido, error = validate_cif(documento)
            if not valido:
                return False, f"NIF-IVA inválido: {error}"
        elif re.match(r'^[XYZ]\d{7}[A-Z]$', documento):
            # Es un NIE
            valido, error = validate_nie(documento)
            if not valido:
                return False, f"NIF-IVA inválido: {error}"
        else:
            return False, "Formato inválido. Para España (ES) debe ser seguido de NIF, CIF o NIE válido"
    else:
        # Para otros países, solo validar formato básico
        # El documento debe tener al menos 2 caracteres y ser alfanumérico
        if len(documento) < 2:
            return False, f"El número de identificación de {codigo_pais} debe tener al menos 2 caracteres"
        if not re.match(r'^[A-Z0-9]+$', documento):
            return False, f"El número de identificación de {codigo_pais} solo puede contener letras y números"
        # Validación básica: no podemos validar algoritmos de control de otros países
        # pero verificamos que tenga un formato razonable (máximo 15 caracteres es común)
        if len(documento) > 15:
            return False, f"El número de identificación de {codigo_pais} parece demasiado largo (máximo 15 caracteres)"
    
    return True, None


def validate_documento(documento: str, tipo: Optional[str] = None) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Valida un documento de identificación español (NIF, CIF o NIE).
    Intenta detectar automáticamente el tipo si no se especifica.
    
    Args:
        documento: Documento a validar
        tipo: Tipo de documento ('NIF', 'CIF', 'NIE', 'NIF-IVA') o None para auto-detectar
    
    Returns:
        Tuple[bool, Optional[str], Optional[str]]: (es_válido, mensaje_error, tipo_detectado)
    """
    if not documento:
        return False, "Documento vacío", None
    
    doc_clean = re.sub(r'[\s\-\._]', '', str(documento).strip().upper())
    
    # Si se especifica el tipo, validar directamente
    if tipo:
        tipo_upper = tipo.upper()
        if tipo_upper == 'NIF':
            valido, error = validate_nif(doc_clean)
            return valido, error, 'NIF'
        elif tipo_upper == 'CIF':
            valido, error = validate_cif(doc_clean)
            return valido, error, 'CIF'
        elif tipo_upper == 'NIE':
            valido, error = validate_nie(doc_clean)
            return valido, error, 'NIE'
        elif tipo_upper in ('NIF-IVA', 'NIFIVA', 'IVA'):
            valido, error = validate_nif_iva(doc_clean)
            return valido, error, 'NIF-IVA'
        else:
            return False, f"Tipo de documento desconocido: {tipo}", None
    
    # Auto-detectar tipo
    # Verificar si empieza por código de país de la UE (2 letras)
    codigos_pais_ue = {
        'AT', 'BE', 'BG', 'CY', 'CZ', 'DE', 'DK', 'EE', 'ES', 'FI', 
        'FR', 'GR', 'HR', 'HU', 'IE', 'IT', 'LT', 'LU', 'LV', 'MT', 
        'NL', 'PL', 'PT', 'RO', 'SE', 'SI', 'SK'
    }
    if len(doc_clean) >= 2 and doc_clean[:2] in codigos_pais_ue and len(doc_clean) > 2:
        # Es un NIF-IVA (cualquier país de la UE)
        valido, error = validate_nif_iva(doc_clean)
        return valido, error, 'NIF-IVA'
    elif re.match(r'^\d{8}[A-Z]$', doc_clean):
        # Es un NIF
        valido, error = validate_nif(doc_clean)
        return valido, error, 'NIF'
    elif re.match(r'^[ABCDEFGHJNPQRSUVW]\d{7}[0-9A-J]$', doc_clean):
        # Es un CIF
        valido, error = validate_cif(doc_clean)
        return valido, error, 'CIF'
    elif re.match(r'^[XYZ]\d{7}[A-Z]$', doc_clean):
        # Es un NIE
        valido, error = validate_nie(doc_clean)
        return valido, error, 'NIE'
    else:
        return False, "Formato no reconocido. Debe ser NIF (8 dígitos + letra), CIF (letra + 7 dígitos + control), NIE (X/Y/Z + 7 dígitos + letra) o NIF-IVA (código país UE + documento)", None


def clean_documento(documento: str) -> str:
    """
    Limpia un documento de identificación eliminando espacios, guiones, etc.
    
    Args:
        documento: Documento a limpiar
    
    Returns:
        str: Documento limpio en mayúsculas
    """
    if not documento:
        return ""
    return re.sub(r'[\s\-\._]', '', str(documento).strip().upper())

