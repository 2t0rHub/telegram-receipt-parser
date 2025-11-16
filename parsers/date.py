import re

PATRONES_FECHA = [
    r"\b\d{1,2}[./-]\d{1,2}[./-]\d{2,4}\b",  # 05/02/2025, 05-02-25
    r"\b\d{4}[./-]\d{1,2}[./-]\d{1,2}\b",    # 2025-02-05
]

def parse_fecha(lines):
    for linea in lines:
        linea_clean = linea.replace('?','0').replace(';',':').replace('|','1')
        for pat in PATRONES_FECHA:
            m = re.search(pat, linea_clean)
            if m:
                return m.group(0)
    return None
