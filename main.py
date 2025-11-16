from pipeline import TicketPipeline
import sys

if __name__ == "__main__":
    ruta = sys.argv[1]


    pipeline = TicketPipeline()
    resultado = pipeline.procesar_ticket(ruta)


    print("=== RESULTADO DEL TICKET ===")
    for k, v in resultado.items():
        print(f"{k}: {v}")