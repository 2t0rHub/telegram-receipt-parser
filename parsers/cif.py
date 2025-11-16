import re
from utils.helpers import fuzzy_in

CLAVES_CIF = ["CIF", "NIF", "C.I.F", "N.I.F", "IDENT", "IDENTIFIC", "EMPRESA"]

# CIF oficial: letra inicial válida + 7 dígitos + letra/dígito final válido
PATRON_CIF = r"[A-HJ-NP-SUVW]\d{7}[0-9A-J]"

def normalizar(texto):
    return "".join(c for c in texto.upper() if c.isalnum())


# ----------------------
# VALIDACIÓN OFICIAL CIF ESPAÑOL
# ----------------------
def validar_cif(cif):
    """
    Validación oficial del dígito de control del CIF.
    Devuelve True si es válido.
    """
    if not re.fullmatch(PATRON_CIF, cif):
        return False

    letra = cif[0]
    nums = cif[1:-1]
    control = cif[-1]

    suma_pares = sum(int(nums[i]) for i in range(1, 7, 2))
    suma_impares = 0

    for i in range(0, 7, 2):
        doble = int(nums[i]) * 2
        suma_impares += (doble // 10) + (doble % 10)

    suma_total = suma_pares + suma_impares
    digito_control = (10 - (suma_total % 10)) % 10
    control_letras = "JABCDEFGHI"

    if letra in "PQSKNW" and control == control_letras[digito_control]:
        return True
    if letra in "ABCDEFGHJUV" and control == str(digito_control):
        return True
    if letra in "ABEH" and control in (str(digito_control), control_letras[digito_control]):
        return True

    return False


# ----------------------
# PARSER PRINCIPAL
# ----------------------
def parse_cif(lines):
    indices_relevantes = []

    for i, linea in enumerate(lines):
        if fuzzy_in(linea.upper(), CLAVES_CIF, umbral=70):
            indices_relevantes.append(i)

    zonas = []
    for idx in indices_relevantes:
        for delta in [-1, 0, 1]:
            if 0 <= idx + delta < len(lines):
                zonas.append(lines[idx + delta])

    if not zonas:
        zonas = lines[:]  # fallback: revisar todo

    candidatos = []
    for linea in zonas:
        limpio = normalizar(linea)
        encontrados = re.findall(PATRON_CIF, limpio)
        candidatos.extend(encontrados)

    # Filtrar por validez real
    válidos = [c for c in candidatos if validar_cif(c)]

    if válidos:
        return válidos[0]

    # Si ninguno válido pero hay candidatos, devolver el mejor guess
    if candidatos:
        return candidatos[0]

    return None
