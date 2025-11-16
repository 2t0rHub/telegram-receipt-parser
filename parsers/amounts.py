import re

PALABRAS_TOTAL = ["TOTAL", "TOT", "TOTA", "IMPORTE", "SUMA", "PRECIO FINAL", "A COBRAR"]

def parse_total(lines, max_reasonable=10000.0):
    total_candidates = []

    # --- 1️⃣ Buscar líneas con 'TOTAL' ---
    for linea in lines:
        linea_upper = linea.upper()
        if any(pal in linea_upper for pal in PALABRAS_TOTAL):
            texto = linea_upper.replace(",", ".")
            texto = re.sub(r'(\d+)\s+(\d{1,2})', r'\1.\2', texto)  # arreglar 10 60 -> 10.60
            numeros = re.findall(r'\d+\.\d{1,2}', texto)
            for n in numeros:
                val = float(n)
                if 0 < val <= max_reasonable:
                    total_candidates.append(val)

    if total_candidates:
        # Devolver el último total encontrado (más abajo en el ticket)
        return total_candidates[-1]

    # --- 2️⃣ Si no hay TOTAL, buscar cualquier número decimal ---
    fallback_candidates = []
    for idx, linea in enumerate(lines):
        texto = linea.upper().replace(",", ".")
        texto = re.sub(r'(\d+)\s+(\d{1,2})', r'\1.\2', texto)
        numeros = re.findall(r'\d+\.\d{1,2}', texto)
        if not numeros:
            continue
        tiene_divisa = "EUR" in texto or "€" in texto
        for n in numeros:
            val = float(n)
            if 0 < val <= max_reasonable:
                fallback_candidates.append({
                    "valor": val,
                    "linea_index": idx,
                    "tiene_divisa": tiene_divisa
                })

    if not fallback_candidates:
        return None

    # Priorizar los que tengan divisa
    with_divisa = [c for c in fallback_candidates if c["tiene_divisa"]]
    if with_divisa:
        # Devolver el que aparece más abajo
        return max(with_divisa, key=lambda c: c["linea_index"])["valor"]

    # Fallback: devolver el último número decimal válido
    return max(fallback_candidates, key=lambda c: c["linea_index"])["valor"]
