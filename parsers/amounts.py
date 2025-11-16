import re
from utils.helpers import normalizar_importe, fuzzy_in

PALABRAS_TOTAL = ["TOTAL", "TOT", "TOTA", "IMPORTE", "SUMA", "PRECIO FINAL", "CAJA", "CAJ"]

def parse_total(lines):
    candidatos = []

    # Buscar primero líneas con palabras TOTAL
    for linea in lines[-15:]:
        if any(fuzzy_in(palabra, linea.upper(), umbral=60) for palabra in PALABRAS_TOTAL):
            # Asegurarse de que es string
            texto_norm = str(linea).replace(",", ".")
            encontrados = re.findall(r'\d+\.\d{2}', texto_norm)
            candidatos.extend(encontrados)

    if candidatos:
        return round(max(map(float, candidatos)), 2)

    # Fallback: buscar cualquier importe con 2 decimales seguido de EUR o €
    for linea in reversed(lines):
        linea_str = str(linea).replace(",", ".")
        match = re.search(r'(\d+\.\d{2})\s*(EUR|€)?', linea_str.upper())
        if match:
            try:
                return round(float(match.group(1)), 2)
            except:
                continue

    return None
