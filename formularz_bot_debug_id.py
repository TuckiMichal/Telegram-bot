from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

# Etapy formularza
DZIEŃ, ZMIANA, KTO_ODDAJE, KOMU = range(4)

# START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("🗓 Na jaki dzień chcesz zgłosić zamianę?")
    return DZIEŃ

async def dzien(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['dzien'] = update.message.text
    await update.message.reply_text("🕐 Na którą zmianę?")
    return ZMIANA

async def zmiana(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['zmiana'] = update.message.text
    await update.message.reply_text("👤 Kto oddaje zmianę?")
    return KTO_ODDAJE

async def kto(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['kto'] = update.message.text
    await update.message.reply_text("➡️ Komu oddajesz zmianę?")
    return KOMU

# FINALNY KROK — tylko do pozyskania ID
async def komu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    chat_id = update.effective_chat.id
    thread_id = update.message.message_thread_id

    await update.message.reply_text(
        f"🆔 chat_id: {chat_id}\n🧵 message_thread_id: {thread_id}"
    )

    return ConversationHandler.END

# Anulowanie
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("❌ Formularz został anulowany.")
    return ConversationHandler.END

# Uruchomienie bota
def main():
    app = ApplicationBuilder().token("8087667975:AAFf3ZrcV4SRD-nMTeldU-a2bw5Ee__CxHQ").build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            DZIEŃ: [MessageHandler(filters.TEXT & ~filters.COMMAND, dzien)],
            ZMIANA: [MessageHandler(filters.TEXT & ~filters.COMMAND, zmiana)],
            KTO_ODDAJE: [MessageHandler(filters.TEXT & ~filters.COMMAND, kto)],
            KOMU: [MessageHandler(filters.TEXT & ~filters.COMMAND, komu)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    app.run_polling()

if __name__ == '__main__':
    main()
