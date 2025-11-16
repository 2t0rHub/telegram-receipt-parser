from utils.helpers import fuzzy_in

DIVISAS = {
    "EUR": ["EUR", "€", "EURO", "E.U.R"],
    "USD": ["USD", "US$", "$", "DOLAR", "DÓLAR"],
    # "GBP": ["GBP", "£", "LIBRA", "LIBRAS"],
    "JPY": ["JPY", "¥", "YEN"],
}

def parse_currency(lines):
    for linea in reversed(lines):
        linea_upper = linea.upper()
        for divisa, variantes in DIVISAS.items():
            for var in variantes:
                if fuzzy_in(var, linea_upper, umbral=70):
                    return divisa
    # Fallback: si no se encuentra ninguna, se puede asumir EUR o None
    return "EUR"
