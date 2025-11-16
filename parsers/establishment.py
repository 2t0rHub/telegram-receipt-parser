from utils.helpers import fuzzy_in

PALABRAS_ESTABLECIMIENTO = [
    "TIENDA","COMERCIO","ALMACÉN","STORE","SHOP","ZARA","MANGO","PRIMARK","CORTE",
    "INGLES","BAR","RESTAURANTE","FNAC","SPRINGFIELD","PULL","BERSHKA","OYSHO",
    "OIL","GAS","OBRAMAT","GASOLINA","DIESEL","MOEVE","BP","PETROPRIX",
    "MERCADONA","SA","S.A.","SL","S.L."
]

EXCLUDE_KEYWORDS = [
    "VISA","MASTERCARD","MAESTRO","CASH","DEBITO","CRÉDITO","CONTACTLESS",
    "CARITAS","BIENVENIDO","GRACIAS","BIZUM","AYUDA","EJEMPLAR","CLIENTE","COMPRA"
]

def parse_establishment(lines):
    # 1️⃣ Buscar líneas que contengan palabras de establecimiento
    for linea in lines:
        linea_upper = str(linea).upper()
        if any(k in linea_upper for k in EXCLUDE_KEYWORDS):
            continue
        if sum(c.isdigit() for c in linea_upper) > 4:
            continue
        if len(linea_upper.strip()) < 3:
            continue
        if any(fuzzy_in(word, linea_upper, umbral=70) for word in PALABRAS_ESTABLECIMIENTO):
            return linea.strip()

    # 2️⃣ Si no hay coincidencias con palabras clave, devolver la primera línea “limpia”
    for linea in lines:
        linea_upper = str(linea).upper()
        if any(k in linea_upper for k in EXCLUDE_KEYWORDS):
            continue
        if sum(c.isdigit() for c in linea_upper) > 4:
            continue
        if len(linea_upper.strip()) < 3:
            continue
        return linea.strip()

    return None
