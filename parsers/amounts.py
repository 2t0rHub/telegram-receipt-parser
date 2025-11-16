import re

PALABRAS_TOTAL = ["TOTAL", "TOT", "TOTA", "IMPORTE", "SUMA", "PRECIO FINAL", "A COBRAR", "CAJA", "PENDIENTE"]

def parse_total(lines, max_reasonable=10000.0):
    total_candidates = []

    # --- 1️⃣ Buscar líneas con 'TOTAL' y combinar con siguiente línea si es necesario ---
    for idx, linea in enumerate(lines):
        linea_upper = linea.upper()
        if any(pal in linea_upper for pal in PALABRAS_TOTAL):
            # Unir línea actual + siguiente para capturar números que están separados
            texto = linea_upper
            if idx + 1 < len(lines):
                texto += " " + lines[idx + 1].upper()

            # Normalizar comas y espacios: "16 ,50" -> "16.50", "10 60" -> "10.60"
            texto = texto.replace(",", ".")
            texto = re.sub(r'(\d+)\s+(\d{1,2})', r'\1.\2', texto)

            numeros = re.findall(r'\d+\.\d{1,2}', texto)
            for n in numeros:
                val = float(n)
                if 0 < val <= max_reasonable:
                    total_candidates.append(val)

    if total_candidates:
        # El último candidato encontrado suele ser el total
        total = total_candidates[-1]
        return f"{total:.2f}"

    # --- 2️⃣ Fallback: buscar cualquier número decimal ---
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

    # --- 3️⃣ Priorizar los que tengan divisa ---
    with_divisa = [c for c in fallback_candidates if c["tiene_divisa"]]
    if with_divisa:
        total = max(with_divisa, key=lambda c: c["linea_index"])["valor"]
        return f"{total:.2f}"

    # --- 4️⃣ Último número decimal válido ---
    total = max(fallback_candidates, key=lambda c: c["linea_index"])["valor"]
    return f"{total:.2f}"
