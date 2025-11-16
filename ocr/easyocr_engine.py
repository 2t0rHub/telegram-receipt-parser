import easyocr


class EasyOCREngine:
    def __init__(self):
        self.reader = easyocr.Reader(['es'])


    def leer_lineas(self, img):
        resultados = self.reader.readtext(img, detail=0, paragraph=False)
        lineas = [r.strip() for r in resultados]
        return lineas


    def leer_detalle(self, img):
        # Devuelve lista con bounding boxes, texto y probabilidad
        resultados = self.reader.readtext(img, detail=1, paragraph=False)
        return resultados