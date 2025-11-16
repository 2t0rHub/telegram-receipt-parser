import re
from utils.helpers import fuzzy_in

# Variantes OCR típicas de "EFECTIVO"
EFECTIVO_VARIANTES = [
    "EFECTIVO", "EFECTIV0", "EFECTIVD",
    "EFECTVIO", "EFEC TIVO", "EFFECTIVO",
    "EFECTI VO", "EFECT", "ERECTIVO",
    "EFECTLVO", "EFECTIVO0"
]

TARJETA_VARIANTES = [
    "VISA", "MASTERCARD", "MAESTRO", "DEBITO", "DEBIT", "CREDIT"
]

def parse_payment(lines):
    lines_upper = [l.upper() for l in lines]

    # 1️⃣ Detectar EFECTIVO primero pero con variantes explícitas, no fuzzy
    for linea in lines_upper:
        for variante in EFECTIVO_VARIANTES:
            if variante in linea:
                return "EFECTIVO"

    # 2️⃣ Detectar tarjetas (VISA, MASTERCARD…) por coincidencia exacta o casi exacta
    for linea in lines_upper:
        for variante in TARJETA_VARIANTES:
            if variante in linea:
                return variante

    # 3️⃣ Último recurso: fuzzy matching PERO con umbral bajo para evitar falsos positivos
    for linea in lines_upper:
        for metodo in TARJETA_VARIANTES:
            if fuzzy_in(metodo, linea, umbral=90):
                return metodo

    # 4️⃣ Si aparece "CAMBIO", es EFECTIVO
    if any("CAMBIO" in l for l in lines_upper):
        return "EFECTIVO"

    return None
