import re

PALABRAS_TOTAL = ["TOTAL", "TOT", "TOTA", "IMPORTE", "SUMA", "PRECIO FINAL", "A COBRAR", "CAJA", "PENDIENTE"]

def parse_total(lines, line_heights=None, max_reasonable=20000.0):
    """
    lines: lista de strings del OCR
    line_heights: lista de enteros/floats indicando la altura de cada línea (opcional)
    max_reasonable: valor máximo que consideramos razonable
    """
    total_candidates = []

    # --- 1️⃣ Buscar líneas con palabras clave TOTAL ---
    for idx, linea in enumerate(lines):
        linea_upper = linea.upper()
        if any(pal in linea_upper for pal in PALABRAS_TOTAL):
            texto = linea_upper
            # También combinar con la siguiente línea por si el número está separado
            if idx + 1 < len(lines):
                texto += " " + lines[idx + 1].upper()

            # Normalizar comas y espacios: "16 ,50" -> "16.50", "10 60" -> "10.60"
            texto = texto.replace(",", ".")
            texto = re.sub(r'(\d+)\s+(\d{1,2})', r'\1.\2', texto)

            numeros = re.findall(r'\d+\.\d{1,2}', texto)
            for n in numeros:
                val = float(n)
                if 0 < val <= max_reasonable:
                    height = line_heights[idx] if line_heights else 0
                    total_candidates.append({
                        "valor": val,
                        "linea_index": idx,
                        "height": height
                    })

    if total_candidates:
        # Escoger el candidato con mayor altura, si hay empate, el último en el ticket
        best = max(total_candidates, key=lambda c: (c["height"], c["linea_index"]))
        return f"{best['valor']:.2f}"

    # --- 2️⃣ Si no hay TOTAL, buscar cualquier número decimal válido con 2 decimales ---
    fallback_candidates = []
    for idx, linea in enumerate(lines):
        texto = linea.replace(",", ".")
        texto = re.sub(r'(\d+)\s+(\d{1,2})', r'\1.\2', texto)
        numeros = re.findall(r'\d+\.\d{1,2}', texto)

        for n in numeros:
            val = float(n)
            if 0 < val <= max_reasonable:
                height = line_heights[idx] if line_heights else 0
                fallback_candidates.append({
                    "valor": val,
                    "linea_index": idx,
                    "height": height
                })

    if fallback_candidates:
        # Escoger el que tenga mayor altura, si empate el que aparece más abajo
        best = max(fallback_candidates, key=lambda c: (c["height"], c["linea_index"]))
        return f"{best['valor']:.2f}"

    # --- 3️⃣ Si no hay nada ---
    return None
