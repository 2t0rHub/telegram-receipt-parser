import os
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from pipeline import TicketPipeline
from dotenv import load_dotenv
from logger_config import log, log_ticket_success, log_ticket_error

# 🔑 Cargar variables desde .env
load_dotenv()  # Busca automáticamente un archivo .env en el directorio actual

# Variables obligatorias
REQUIRED_ENV_VARS = ["BOT_TOKEN"]

# Comprobar si existen
missing_vars = [var for var in REQUIRED_ENV_VARS if os.getenv(var) is None]
if missing_vars:
    log.critical(f"Faltan variables de entorno obligatorias: {', '.join(missing_vars)}")
    raise RuntimeError(f"\n⚠️ Faltan variables de entorno obligatorias: {', '.join(missing_vars)}")

# Variables seguras
BOT_TOKEN = os.getenv("BOT_TOKEN")
TICKETS_DIR = os.getenv("TICKETS_DIR", "tickets")
os.makedirs(TICKETS_DIR, exist_ok=True)

# Estado temporal de tickets por usuario
user_tickets = {}

# Inicializamos pipeline OCR
pipeline = TicketPipeline()

# --- Función auxiliar para logging ---
def get_user_info(user: Update.effective_user) -> str:
    """Devuelve una cadena de texto identificando al usuario para los logs."""
    user_info = f"ID: {user.id}"
    
    # Construir el nombre completo a partir de first_name y last_name
    name_parts = []
    if user.first_name:
        name_parts.append(user.first_name)
    if user.last_name:
        name_parts.append(user.last_name)
    full_name = " ".join(name_parts).strip()

    # Priorizar @username, si no, usar el nombre completo
    if user.username:
        user_info += f" (@{user.username})"
    elif full_name:
        user_info += f" ({full_name})"
    return user_info

# --- Comandos básicos ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 *¡Hola!*\n\n"
        "Envíame una foto de tu ticket y procesaré los campos automáticamente.\n\n"
        "Puedes editar un campo con `/editar campo valor`, por ejemplo:\n"
        "> /editar total 5.15",
        parse_mode="Markdown"
    )
    log.info(f"User {get_user_info(update.effective_user)} executed /start.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📸 Envía una foto de tu ticket y te devolveré los campos extraídos.\n\n"
        "📝 Para modificar algún campo puedes usar:\n"
        "`/editar campo valor`",
        parse_mode="Markdown"
    )

    log.info(f"User {get_user_info(update.effective_user)} executed /help.")
# --- Función para crear texto bonito con emojis ---
def format_ticket(ticket: dict) -> str:
    result = (
        f"🛒 *Ticket procesado* 🛒\n\n"
        f"🏬 *Establecimiento:* {ticket.get('establecimiento') or '_No encontrado_'}\n"
        f"🆔 *CIF/NIF:* {ticket.get('cif') or '_No encontrado_'}\n"
        f"📅 *Fecha:* {ticket.get('fecha') or '_No encontrada_'}\n"
        f"💰 *Total:* {ticket.get('total') or '_No encontrado_'}\n"
        f"💱 *Divisa:* {ticket.get('divisa') or '_No encontrada_'}\n"
        f"💲 *IVA (%):* {ticket.get('iva') or '_No encontrado_'}\n"
        f"💳 *Método de pago:* {ticket.get('metodo_pago') or '_No encontrado_'}\n\n"
        f"📝 _Si algún campo es incorrecto, puedes editarlo con_ `/editar campo valor`"
    )
    return result

# --- Manejo de imágenes ---
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_info = get_user_info(update.effective_user)
    log.info(f"Photo received from user {user_info}.")
    try:
        await update.message.reply_text("✅ Ticket recibido. Procesando...")

        # Guardar la foto original
        photo = update.message.photo[-1]  # mayor resolución
        file = await context.bot.get_file(photo.file_id)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{TICKETS_DIR}/{timestamp}_{user.id}.jpg"
        await file.download_to_drive(filename)

        # Procesar ticket
        # Asumimos que el pipeline devuelve tanto el resultado procesado como el texto crudo del OCR
        resultado, ocr_text = pipeline.procesar_ticket(filename)
        user_tickets[user.id] = resultado
        
        # Usamos el nuevo sistema de logging para tickets
        # Esto guardará el resultado en 'processed.log' y el texto OCR en 'ocr.log'
        log_ticket_success(user, resultado, ocr_text=ocr_text)

        # Mostrar resultado
        await update.message.reply_text(format_ticket(resultado), parse_mode="Markdown")

    except Exception as e:
        # Loguear el error general en bot.log
        log.error(f"Error processing photo for user {user_info}: {e}", exc_info=False) # exc_info=False para no duplicar stack trace
        # Usar el nuevo sistema de logging para errores de ticket
        log_ticket_error(user, error_message=str(e))
        await update.message.reply_text(f"⚠️ Error procesando la imagen: {e}")

# --- Comando /editar ---
async def editar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_info = get_user_info(update.effective_user)
    try:
        log.info(f"User {user_info} is using /editar with args: {context.args}")
        args = context.args
        if len(args) < 2:
            await update.message.reply_text("Uso: `/editar campo valor`", parse_mode="Markdown")
            return

        campo = args[0].lower()
        valor = " ".join(args[1:])
        ticket = user_tickets.get(update.effective_user.id)

        if not ticket:
            await update.message.reply_text("_No hay ticket procesado para editar._", parse_mode="Markdown")
            return

        if campo not in ticket:
            await update.message.reply_text(f"_Campo '{campo}' no existe._", parse_mode="Markdown")
            return

        ticket[campo] = valor

        log.info(f"User {user_info} updated field '{campo}' to '{valor}'.")
        # Mostrar ticket actualizado
        await update.message.reply_text(
            f"✅ Campo '*{campo}*' actualizado a '*{valor}*'.\n\n{format_ticket(ticket)}",
            parse_mode="Markdown"
        )

    except Exception as e:
        log.error(f"Error in /editar for user {user_info}: {e}", exc_info=True)
        await update.message.reply_text(f"Error: {e}")

# --- Main ---
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("editar", editar))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    log.info("Bot started. Polling for updates...")
    app.run_polling()
