import numpy as np

def recorte_superior(img):
    h = img.shape[0]
    return img[: int(h * 0.25), :]