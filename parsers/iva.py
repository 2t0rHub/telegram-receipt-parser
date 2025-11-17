import re
from decimal import Decimal, ROUND_HALF_UP

IVA_PATTERNS = {
    # Patrones más flexibles para diferentes formatos
    'percentage': [
        r'IVA\s*[:\-]?\s*(\d+[.,]?\d*)\s*%',
        r'(\d+[.,]?\d*)\s*%\s*IVA',
        r'IVA\s*\((\d+[.,]?\d*)%\)',
        r'IMPUESTO.*?(\d+[.,]?\d*)\s*%',
    ],
    'separate_line': [
        r'^IVA\s+(\d+[.,]?\d*)$',
        r'^.*IVA.*?(\d+[.,]?\d*)$',
    ],
    'calculation': [
        r'(\d+[.,]?\d*)\s*\+\s*IVA',
        r'BASE\s*[:\-]?\s*(\d+[.,]?\d*).*IVA\s*[:\-]?\s*(\d+[.,]?\d*)',
    ]
}

# Valores estándar de IVA en España (con tolerancia)
STANDARD_IVA = [4.0, 10.0, 21.0]
TOLERANCE = 0.5  # ±0.5% para ajustar errores de OCR

def parse_iva_improved(lines):
    """
    Estrategia mejorada para detectar IVA con múltiples enfoques.
    """
    full_text = " ".join(lines)
    
    # Método 1: Búsqueda directa con patrones flexibles
    iva_value = find_iva_with_patterns(full_text, lines)
    if iva_value:
        return iva_value
    
    # Método 2: Análisis de estructura de precios
    iva_value = analyze_price_structure(lines)
    if iva_value:
        return iva_value
        
    # Método 3: Búsqueda contextual ampliada
    iva_value = contextual_search(lines)
    if iva_value:
        return iva_value
        
    return None

def find_iva_with_patterns(full_text, lines):
    """Busca IVA usando múltiples patrones regex"""
    
    # Patrones de porcentaje
    percentage_patterns = [
        r'IVA\s*[:\-]?\s*(\d+[.,]?\d*)\s*[%％]',
        r'(\d+[.,]?\d*)\s*[%％]\s*IVA',
        r'IVA\s*\(?\s*(\d+[.,]?\d*)\s*[%％]\s*\)?',
        r'IMPUESTO.*?(\d+[.,]?\d*)\s*[%％]',
        r'V\.?A\.?T\.?\s*[:\-]?\s*(\d+[.,]?\d*)\s*[%％]',
    ]
    
    for pattern in percentage_patterns:
        matches = re.findall(pattern, full_text, re.IGNORECASE)
        for match in matches:
            try:
                value = float(match.replace(',', '.'))
                # Verificar si es un valor estándar (con tolerancia)
                for standard in STANDARD_IVA:
                    if abs(value - standard) <= TOLERANCE:
                        return standard
                # Si no es estándar pero está en rango plausible, devolverlo redondeado
                if 1 <= value <= 30:
                    return round(value)
            except (ValueError, TypeError):
                continue
    
    return None

def analyze_price_structure(lines):
    """
    Analiza la estructura de precios para inferir el IVA.
    Busca patrones como: base + IVA = total
    """
    price_pattern = r'(\d+[.,]?\d*[.,]?\d*)'  # Más flexible para formatos de precio
    
    for i, line in enumerate(lines):
        line_clean = re.sub(r'[^\d\s.,]', ' ', line)  # Solo números y separadores
        numbers = re.findall(price_pattern, line_clean)
        
        if len(numbers) >= 3:
            # Intentar encontrar base, IVA y total
            numbers_float = []
            for n in numbers:
                try:
                    # Manejar diferentes formatos de decimales
                    if ',' in n and '.' in n:
                        # Formato europeo: 1.234,56
                        n = n.replace('.', '').replace(',', '.')
                    elif ',' in n:
                        # Posible decimal con coma
                        n = n.replace(',', '.')
                    numbers_float.append(float(n))
                except ValueError:
                    continue
            
            if len(numbers_float) >= 3:
                # Buscar combinaciones que coincidan con IVA estándar
                for j in range(len(numbers_float) - 2):
                    base, iva_amount, total = numbers_float[j], numbers_float[j+1], numbers_float[j+2]
                    
                    if base > 0 and abs(total - (base + iva_amount)) < 0.01:
                        calculated_pct = (iva_amount / base) * 100
                        
                        # Verificar contra valores estándar
                        for standard in STANDARD_IVA:
                            if abs(calculated_pct - standard) <= TOLERANCE:
                                return standard
                
                # Buscar patrones de cálculo directo
                for j in range(len(numbers_float) - 1):
                    base, total = numbers_float[j], numbers_float[j+1]
                    if base > 0 and total > base:
                        calculated_pct = ((total - base) / base) * 100
                        
                        for standard in STANDARD_IVA:
                            if abs(calculated_pct - standard) <= TOLERANCE:
                                return standard
    
    return None

def contextual_search(lines):
    """
    Búsqueda contextual más amplia - busca líneas que contengan
    keywords de IVA y analiza el contexto cercano
    """
    iva_keywords = ['IVA', 'IMPUESTO', 'V.A.T', 'VAT', 'I.V.A', 'TAX']
    
    for i, line in enumerate(lines):
        line_upper = line.upper()
        
        # Verificar si la línea contiene algún keyword
        has_keyword = any(keyword in line_upper for keyword in iva_keywords)
        
        if has_keyword:
            # Buscar porcentajes en la misma línea
            percentages = re.findall(r'(\d+[.,]?\d*)\s*[%％]', line)
            for pct in percentages:
                try:
                    value = float(pct.replace(',', '.'))
                    for standard in STANDARD_IVA:
                        if abs(value - standard) <= TOLERANCE:
                            return standard
                except ValueError:
                    continue
            
            # Buscar en líneas adyacentes
            for offset in [-1, 1, -2, 2]:  # Líneas anterior, siguiente, etc.
                idx = i + offset
                if 0 <= idx < len(lines):
                    adjacent_line = lines[idx]
                    percentages = re.findall(r'(\d+[.,]?\d*)\s*[%％]', adjacent_line)
                    for pct in percentages:
                        try:
                            value = float(pct.replace(',', '.'))
                            for standard in STANDARD_IVA:
                                if abs(value - standard) <= TOLERANCE:
                                    return standard
                        except ValueError:
                            continue
    
    return None

# Función principal mejorada
def parse_iva(lines):
    """
    Versión mejorada que combina múltiples estrategias
    """
    result = parse_iva_improved(lines)
    
    # Post-procesamiento: asegurar que sea un valor estándar
    if result:
        # Redondear al valor estándar más cercano
        closest_standard = min(STANDARD_IVA, key=lambda x: abs(x - result))
        if abs(closest_standard - result) <= 2:  # Tolerancia más amplia
            return closest_standard
        elif 1 <= result <= 30:  # Rango plausible pero no estándar
            return round(result)
    
    return None