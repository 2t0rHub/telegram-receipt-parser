def construir_lineas(ocr_result, y_threshold=12):
    """
    Ordena y agrupa las palabras detectadas por EasyOCR en líneas reales.
    Devuelve una lista de diccionarios con:
        { "texto": "...", "x": ?, "y": ?, "w": ?, "h": ? }
    """

    palabras = []

    # Convertir bounding boxes a objetos con coordenadas simples
    for (bbox, text, prob) in ocr_result:
        (x1, y1), (x2, y2), (x3, y3), (x4, y4) = bbox
        x = min(x1, x2, x3, x4)
        y = min(y1, y2, y3, y4)
        w = max(x1, x2, x3, x4) - x
        h = max(y1, y2, y3, y4) - y

        palabras.append({
            "text": text,
            "x": x,
            "y": y,
            "w": w,
            "h": h
        })

    # Orden por Y, luego por X
    palabras.sort(key=lambda p: (p["y"], p["x"]))

    # Agrupar en líneas verdaderas
    lineas = []
    linea_actual = []
    last_y = None

    for p in palabras:
        if last_y is None:
            linea_actual.append(p)
            last_y = p["y"]
            continue

        if abs(p["y"] - last_y) <= y_threshold:
            linea_actual.append(p)
        else:
            # Cerrar línea y abrir otra
            lineas.append(sorted(linea_actual, key=lambda p: p["x"]))
            linea_actual = [p]

        last_y = p["y"]

    if linea_actual:
        lineas.append(sorted(linea_actual, key=lambda p: p["x"]))

    # Convertir líneas a texto limpio
    lineas_texto = [" ".join([p["text"] for p in linea]) for linea in lineas]

    return lineas_texto, lineas
