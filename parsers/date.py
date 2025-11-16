import re
from datetime import datetime
from utils.helpers import fuzzy_in

PATRONES_NUMERICOS = [
    r"(?P<d>\d{1,2})[./\-]\s*(?P<m>\d{1,2})[./\-]\s*(?P<y>\d{2,4})",
    r"(?P<y>\d{4})[./\-]\s*(?P<m>\d{1,2})[./\-]\s*(?P<d>\d{1,2})",
]

MONTH_MAP = {
    1: ["ENERO", "ENE", "JAN"],
    2: ["FEBRERO", "FEB"],
    3: ["MARZO", "MAR", "MARCH"],
    4: ["ABRIL", "ABR", "APR"],
    5: ["MAYO", "MAY"],
    6: ["JUNIO", "JUN", "JUNE"],
    7: ["JULIO", "JUL", "JULY"],
    8: ["AGOSTO", "AGO", "AUG"],
    9: ["SEPTIEMBRE", "SEP", "SEPT"],
    10: ["OCTUBRE", "OCT"],
    11: ["NOVIEMBRE", "NOV"],
    12: ["DICIEMBRE", "DIC", "DEC"]
}

def _expand_two_digit_year(y):
    """Solo expande si es año de 2 dígitos"""
    y = int(y)
    return 1900 + y if 50 <= y <= 99 else 2000 + y if 0 <= y <= 49 else y

def _validated_date(day, month, year):
    """Versión robusta que maneja meses en texto y años de 2 dígitos"""
    try:
        # Convertir mes si es texto
        if isinstance(month, str) and not month.isdigit():
            month_upper = month.strip().upper()
            found = False
            for mnum, variants in MONTH_MAP.items():
                for var in variants:
                    if month_upper.startswith(var[:3]):  # Primeros 3 caracteres
                        month = mnum
                        found = True
                        break
                if found:
                    break
            if not found:
                return None  # No se encontró mes válido

        day, month, year = int(day), int(month), int(year)
        if 0 <= year <= 99:
            year = _expand_two_digit_year(year)

        if not (1900 <= year <= datetime.now().year):
            return None
        if not (1 <= month <= 12):
            return None
        if not (1 <= day <= 31):
            return None

        fecha = datetime(year, month, day)
        if fecha > datetime.now():
            return None

        return fecha.strftime("%d/%m/%Y")
    except:
        return None

def parse_fecha(lines):
    """Detecta cualquier tipo de fecha: numérica o con meses escritos"""
    texto = " ".join(str(line) for line in lines if line)

    # 1️⃣ Fechas con mes escrito (ej: 16/ mar / 2025, 16-Mar-25, 16 . March . 2025)
    text_pattern = r"(\d{1,2})\s*[./\-]?\s*([a-záéíóúñ]{3,})\s*[./\-]?\s*(\d{2,4})"
    match = re.search(text_pattern, texto, re.IGNORECASE)
    if match:
        day, month, year = match.groups()
        fecha = _validated_date(day, month, year)
        if fecha:
            return fecha

    # 2️⃣ Fechas numéricas
    for pat in PATRONES_NUMERICOS:
        match = re.search(pat, texto)
        if match:
            groups = match.groupdict()
            fecha = _validated_date(groups['d'], groups['m'], groups['y'])
            if fecha:
                return fecha

    return None
