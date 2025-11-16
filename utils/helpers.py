import re
from rapidfuzz import fuzz, process
import difflib

def fuzzy_in(text, candidates, umbral=75):
    """
    Devuelve True si 'text' es parecida a alguna palabra en candidates.
    Usa rapidfuzz si está disponible; si no, difflib.
    """
    if not text:
        return False

    try:
        best = process.extractOne(text, candidates, scorer=fuzz.partial_ratio)
        return best and best[1] >= umbral
    except Exception:
        # fallback si rapidfuzz fallara
        best = difflib.get_close_matches(text, candidates, n=1, cutoff=umbral/100)
        return len(best) > 0
    
import re

def normalizar_importe(texto: str) -> float:
    """
    Normaliza un importe detectado por OCR y lo convierte a float con 2 decimales.
    
    Ejemplos:
        "90 00 EUR" -> 90.00
        "123,45 USD" -> 123.45
        "1 234,56 €" -> 1234.56
        "12,5" -> 12.50
    
    Args:
        texto (str): texto OCR detectado
    
    Returns:
        float: importe normalizado
    """
    if not texto:
        return 0.0
    
    texto = texto.upper()
    
    # Eliminar símbolos de divisa
    texto = re.sub(r"(EUR|€|USD|US\$|GBP|£)", "", texto)
    
    # Reemplazar coma decimal por punto
    texto = texto.replace(',', '.')
    
    # Unir números separados por espacios o puntos intermedios (ej: '90 00' -> '90.00')
    texto = re.sub(r'(\d+)[ .](\d{2})', r'\1.\2', texto)
    
    # Eliminar espacios sobrantes
    texto = texto.replace(' ', '')
    
    try:
        return round(float(texto), 2)
    except:
        return 0.0
