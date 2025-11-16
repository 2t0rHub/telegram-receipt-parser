import os
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from pipeline import TicketPipeline
from dotenv import load_dotenv

# Cargar variables desde .env
load_dotenv()  # Busca automáticamente un archivo .env en el directorio actual

# Variables obligatorias
REQUIRED_ENV_VARS = ["BOT_TOKEN"]

# Comprobar si existen
missing_vars = [var for var in REQUIRED_ENV_VARS if os.getenv(var) is None]
if missing_vars:
    raise RuntimeError(f"\n ⚠️ Faltan variables de entorno obligatorias: {', '.join(missing_vars)}")

# Variables obligatorias seguras
BOT_TOKEN = os.getenv("BOT_TOKEN")
TICKETS_DIR = os.getenv("TICKETS_DIR")
# 📁 Carpeta donde se guardarán los tickets
TICKETS_DIR = os.getenv("TICKETS_DIR", "tickets")
os.makedirs(TICKETS_DIR, exist_ok=True)

# Estado temporal de tickets por usuario
user_tickets = {}

# Inicializamos pipeline OCR
pipeline = TicketPipeline()

# --- Comandos básicos ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 ¡Hola! Envíame una foto de tu ticket y procesaré los campos automáticamente.\n"
        "Puedes editar un campo con /editar campo valor, por ejemplo:\n"
        "/editar total 7.72"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📸 Solo tienes que enviarme una foto del ticket y te devolveré los campos extraídos."
    )

# --- Función para crear texto bonito con emojis ---
def format_ticket(ticket: dict) -> str:
    return (
        f"🛒 **Ticket procesado** 🛒\n\n"
        f"🏬 Establecimiento: {str(ticket.get('establecimiento') or '')}\n"
        f"🆔 CIF/NIF: {str(ticket.get('cif') or 'No encontrado')}\n"
        f"📅 Fecha: {str(ticket.get('fecha') or 'No encontrada')}\n"
        f"💰 Total: {str(ticket.get('total') or 'No encontrado')}\n"
        f"💱 Divisa: {str(ticket.get('divisa') or 'No encontrada')}\n"
        f"💳 Método de pago: {str(ticket.get('metodo_pago') or 'No encontrado')}"
    )

# --- Manejo de imágenes ---
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_text("✅ Ticket recibido. Procesando...")

        # Guardar la foto original
        photo = update.message.photo[-1]  # mayor resolución
        file = await context.bot.get_file(photo.file_id)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{TICKETS_DIR}/{timestamp}_{update.message.from_user.id}.jpg"
        await file.download_to_drive(filename)

        # Procesar ticket
        resultado = pipeline.procesar_ticket(filename)
        user_tickets[update.message.from_user.id] = resultado

        # Mostrar resultado
        await update.message.reply_text(format_ticket(resultado), parse_mode="Markdown")

    except Exception as e:
        await update.message.reply_text(f"⚠️ Error procesando la imagen: {e}")


# --- Comando /editar ---
async def editar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        args = context.args
        if len(args) < 2:
            await update.message.reply_text("Uso: /editar campo valor")
            return

        campo = args[0].lower()
        valor = " ".join(args[1:])
        ticket = user_tickets.get(update.message.from_user.id)

        if not ticket:
            await update.message.reply_text("No hay ticket procesado para editar.")
            return

        if campo not in ticket:
            await update.message.reply_text(f"Campo '{campo}' no existe.")
            return

        ticket[campo] = valor

        # Mostrar ticket actualizado
        await update.message.reply_text(
            f"✅ Campo '{campo}' actualizado a '{valor}'.\n\n{format_ticket(ticket)}",
            parse_mode="Markdown"
        )

    except Exception as e:
        await update.message.reply_text(f"Error: {e}")


# --- Main ---
if __name__ == "__main__":
    from telegram.ext import ApplicationBuilder

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("editar", editar))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    print("🤖 Bot en marcha... esperando fotos de tickets.")
    app.run_polling()

