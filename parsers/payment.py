# parsers/payment.py
from utils.helpers import fuzzy_in

METODOS_PAGO = ["VISA","MASTERCARD","MAESTRO","AMEX","DINERS","CASH","CONTACTLESS","DEBITO"]

def parse_payment(lines):
    for linea in lines:
        for metodo in METODOS_PAGO:
            if fuzzy_in(metodo, linea.upper(), umbral=70):
                return metodo
    return None
