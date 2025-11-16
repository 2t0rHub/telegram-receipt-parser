from utils.helpers import fuzzy_in

METODOS_PAGO = ["EFECTIVO", "VISA", "MASTERCARD", "MAESTRO", "CASH", "CONTACTLESS", "DEBITO"]

def parse_payment(lines):
    for linea in lines:
        linea_upper = linea.upper()
        # Primero buscamos coincidencias aproximadas con los métodos de pago
        for metodo in METODOS_PAGO:
            if fuzzy_in(metodo, linea_upper, umbral=80):
                return metodo
    
    # Si no encuentra nada, buscamos "CAMBIO" en alguna línea
    for linea in lines:
        if "CAMBIO" in linea.upper():
            return "EFECTIVO"
    
    return None
