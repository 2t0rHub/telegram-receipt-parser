from preprocess.filters import preprocesar_imagen
from ocr.easyocr_engine import EasyOCREngine
from ocr.segmenters import recorte_superior
from utils.ocr_structure import construir_lineas
from parsers.establishment import parse_establishment
from parsers.cif import parse_cif
from parsers.date import parse_fecha
from parsers.amounts import parse_total
from parsers.payment import parse_payment
from parsers.currency import parse_currency  # <-- nuevo

class TicketPipeline:

    def __init__(self):
        self.ocr = EasyOCREngine()

    def procesar_ticket(self, ruta_imagen):
        img = preprocesar_imagen(ruta_imagen)

        # OCR completo con bounding boxes
        ocr_result = self.ocr.leer_detalle(img)  # [(bbox, texto, prob)]

        # Construir líneas ordenadas por posición (arriba a abajo)
        lines, raw_lines = construir_lineas(ocr_result)

        # OCR específico para encabezado (arriba)
        img_top = recorte_superior(img)
        ocr_result_top = self.ocr.leer_detalle(img_top)
        lines_top, _ = construir_lineas(ocr_result_top)

        # Combinar líneas
        todas_las_lineas = lines_top + lines

        # --- Parseos robustos ---
        nombre = parse_establishment(todas_las_lineas)
        cif = parse_cif(todas_las_lineas)
        fecha = parse_fecha(todas_las_lineas)
        total = parse_total(todas_las_lineas)
        metodo_pago = parse_payment(todas_las_lineas)
        divisa = parse_currency(todas_las_lineas)  # <-- nuevo

        # --- Construir diccionario antes del return ---
        resultado = {
            "establecimiento": nombre,
            "cif": cif,
            "fecha": fecha,
            "total": total,
            "divisa": divisa,          # <-- añadido
            "metodo_pago": metodo_pago
        }

        # --- Debug ---
        print(todas_las_lineas)

        return resultado
