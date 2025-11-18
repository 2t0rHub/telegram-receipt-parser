import logging
import os
import json
import uuid
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime

# --- Constantes de Configuración ---
LOGS_DIR = 'logs'
TICKETS_LOGS_DIR = os.path.join(LOGS_DIR, 'tickets')
BACKUP_COUNT = 7  # Días de logs a conservar

# --- Creación de Directorios ---
os.makedirs(TICKETS_LOGS_DIR, exist_ok=True)

# --- Formateador JSON ---
class JsonFormatter(logging.Formatter):
    """Formatea los registros como una cadena JSON por línea."""
    def format(self, record):
        # El mensaje ya viene como un diccionario
        log_record = record.msg
        log_record['timestamp'] = datetime.utcfromtimestamp(record.created).isoformat() + 'Z'
        return json.dumps(log_record, ensure_ascii=False)

# --- Función Fábrica para Loggers ---
def create_logger(name, log_file, level=logging.INFO, formatter=None, is_json=False):
    """Crea y configura un logger con rotación diaria."""
    handler = TimedRotatingFileHandler(log_file, when="midnight", interval=1, backupCount=BACKUP_COUNT, encoding='utf-8')
    
    if is_json:
        handler.setFormatter(JsonFormatter())
    elif formatter:
        handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False
    if not logger.handlers:
        logger.addHandler(handler)
    return logger

# --- Creación de los Loggers Específicos ---

# 1. Logger General (bot.log)
general_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
)
log = create_logger(
    'general_bot',
    os.path.join(LOGS_DIR, 'bot.log'),
    formatter=general_formatter
)

# 2. Logger de Tickets Procesados (tickets/processed_YYYY-MM-DD.log)
success_logger = create_logger(
    'ticket_success',
    os.path.join(TICKETS_LOGS_DIR, 'processed.log'),
    is_json=True
)

# 3. Logger de OCR (tickets/ocr_YYYY-MM-DD.log)
ocr_logger = create_logger(
    'ticket_ocr',
    os.path.join(TICKETS_LOGS_DIR, 'ocr.log'),
    is_json=True
)

# 4. Logger de Errores (tickets/errors_YYYY-MM-DD.log)
error_logger = create_logger(
    'ticket_error',
    os.path.join(TICKETS_LOGS_DIR, 'errors.log'),
    is_json=True
)

# --- Funciones Auxiliares de Logging ---

def _get_user_details(user):
    """Extrae un diccionario con los detalles del usuario."""
    return {
        "user_id": user.id,
        "username": user.username,
        "first_name": user.first_name
    }

def log_ticket_success(user, ticket_result, ocr_text=None):
    """Registra un ticket procesado correctamente y su OCR."""
    ticket_id = str(uuid.uuid4())
    user_details = _get_user_details(user)

    # Log del ticket procesado
    # Esta entrada contiene el resultado del parseo
    success_log_entry = {
        "ticket_id": ticket_id,
        "user": user_details,
        "status": "success",
        "result": ticket_result
    }
    success_logger.info(success_log_entry)

    # Log del texto OCR si está disponible.
    # Esta entrada contiene el texto crudo extraído por el OCR.
    if ocr_text:
        ocr_log_entry = {
            "ticket_id": ticket_id,
            "user": user_details,
            "raw_text": ocr_text
        }
        ocr_logger.info(ocr_log_entry)

def log_ticket_error(user, error_message, raw_data=None):
    """Registra un fallo en el procesamiento de un ticket."""
    # Se genera un ID único para cada error para poder rastrearlo
    ticket_id = str(uuid.uuid4())
    user_details = _get_user_details(user)
    
    error_log_entry = {
        "ticket_id": ticket_id,
        "user": user_details,
        "status": "error",
        "error_description": str(error_message),
        "raw_data": raw_data
    }
    error_logger.info(error_log_entry)
