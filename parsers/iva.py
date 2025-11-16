import re
from utils.helpers import fuzzy_in

IVA_KEYWORDS = [
    "IVA", "I.V.A", "IMPUESTO", "Iva", "Iva incluido", "V.A.T", "vat", "VAT"
]

STANDARD_IVA = [4, 10, 21]  # Valores comunes en España

def parse_iva(lines):
    """
    Detecta el porcentaje de IVA en un ticket usando keywords y fuzzy matching.
    Retorna un int (ej: 10, 21) o None si no se encuentra.
    """
    def extract_candidates(line):
        # Extraer números aunque tengan separadores extraños
        nums = re.findall(r'\d+[.,]?\d*', line)
        nums = [float(n.replace(',', '.')) for n in nums]
        candidates = []
        for i in range(len(nums) - 1):
            base, iva = nums[i], nums[i + 1]
            if base > 0:
                pct = round((iva / base) * 100)
                if 3 <= pct <= 30:  # Plausible
                    candidates.append(pct)
        return candidates

    for i, line in enumerate(lines):
        line_upper = line.upper()
        if any(fuzzy_in(keyword.upper(), line_upper, 70) for keyword in IVA_KEYWORDS):
            candidates = extract_candidates(line)
            # Revisar línea siguiente por si los números están ahí
            if i + 1 < len(lines):
                candidates += extract_candidates(lines[i + 1])
            if candidates:
                # Escoger el candidato más cercano a los valores estándar
                closest = min(candidates, key=lambda x: min(abs(x - s) for s in STANDARD_IVA))
                # Ajustar ±2% errores OCR
                for s in STANDARD_IVA:
                    if abs(closest - s) <= 2:
                        closest = s
                        break
                return closest

    return None
