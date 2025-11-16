import cv2
import numpy as np


def preprocesar_imagen(image_path: str, scale_factor: int = 2) -> np.ndarray:
    try:
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"No se pudo cargar la imagen: {image_path}")

        # Escalar primero si es necesario
        if scale_factor > 1:
            height, width = image.shape[:2]
            new_width = width * scale_factor
            new_height = height * scale_factor
            image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_CUBIC)

        # Convertir a gris
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Mejorar contraste local con CLAHE
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        gray = clahe.apply(gray)

        # Suavizado ligero para reducir ruido sin perder bordes
        gray = cv2.GaussianBlur(gray, (3, 3), 0)

        return gray

    except Exception as e:
        print(f"Error en preprocesamiento: {e}")
        return None
