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
os.makedirs(os.path.join(TICKETS_LOGS_DIR, 'processed'), exist_ok=True)
os.makedirs(os.path.join(TICKETS_LOGS_DIR, 'ocr'), exist_ok=True)
os.makedirs(os.path.join(TICKETS_LOGS_DIR, 'errors'), exist_ok=True)


# --- Formateador JSON ---
class JsonFormatter(logging.Formatter):
    """Formatea los registros como una cadena JSON por línea."""
    def format(self, record):
        log_record = record.msg
        log_record['timestamp'] = datetime.utcfromtimestamp(record.created).strftime("%Y-%m-%dT%H:%M:%SZ")
        return json.dumps(log_record, ensure_ascii=False)

# --- Función Fábrica para Loggers ---
def create_logger(name, log_file, level=logging.INFO, formatter=None, is_json=False, rotate=False):
    """Crea y configura un logger.
    Si rotate=True, se hace rotación diaria (solo para bot.log)."""
    if rotate:
        handler = TimedRotatingFileHandler(
            log_file, when="midnight", interval=1, backupCount=BACKUP_COUNT, encoding='utf-8'
        )
    else:
        handler = logging.FileHandler(log_file, encoding='utf-8')
    
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

# --- Fecha de hoy para logs diarios ---
today = datetime.now().strftime("%d-%m-%Y")

# --- Creación de los Loggers Específicos ---

# 1. Logger General (bot_DD-MM-YYYY.log) con rotación diaria
general_formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%d-%m-%Y %H:%M:%S'
)
general_log_file = os.path.join(LOGS_DIR, f'bot_{today}.log')
log = create_logger(
    'general_bot',
    general_log_file,
    formatter=general_formatter,
    rotate=True
)

# 2. Logger de Tickets Procesados (processed_DD-MM-YYYY.log)
processed_log_file = os.path.join(TICKETS_LOGS_DIR, "processed", f"processed_{today}.log")
success_logger = create_logger(
    'ticket_success',
    processed_log_file,
    is_json=True
)

# 3. Logger de OCR (ocr_DD-MM-YYYY.log)
ocr_log_file = os.path.join(TICKETS_LOGS_DIR, "ocr", f"ocr_{today}.log")
ocr_logger = create_logger(
    'ticket_ocr',
    ocr_log_file,
    is_json=True
)

# 4. Logger de Errores (errors_DD-MM-YYYY.log)
error_log_file = os.path.join(TICKETS_LOGS_DIR, "errors", f"errors_{today}.log")
error_logger = create_logger(
    'ticket_error',
    error_log_file,
    is_json=True
)

# --- Funciones Auxiliares de Logging ---
def _get_user_details(user):
    return {
        "user_id": user.id,
        "username": user.username,
        "first_name": user.first_name
    }

def log_ticket_success(user, ticket_result, ocr_text=None):
    ticket_id = str(uuid.uuid4())
    user_details = _get_user_details(user)

    success_log_entry = {
        "ticket_id": ticket_id,
        "user": user_details,
        "status": "success",
        "result": ticket_result
    }
    success_logger.info(success_log_entry)

    if ocr_text:
        ocr_log_entry = {
            "ticket_id": ticket_id,
            "user": user_details,
            "raw_text": ocr_text
        }
        ocr_logger.info(ocr_log_entry)

def log_ticket_error(user, error_message, raw_data=None):
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
