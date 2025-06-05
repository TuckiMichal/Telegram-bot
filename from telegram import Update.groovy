from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

# Kroki formularza
DZIEŃ, ZMIANA, KTO_ODDAJE, KOMU = range(4)

# TWÓJ ID Telegrama (możesz podać później, na razie ustaw 0)
ADMIN_CHAT_ID = 0

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(f"Twój chat ID to: {update.effective_chat.id}")
    return ConversationHandler.END

async def dzien(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['dzien'] = update.message.text
    await update.message.reply_text("Na którą zmianę?")
    return ZMIANA

async def zmiana(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['zmiana'] = update.message.text
    await update.message.reply_text("Kto oddaje zmianę?")
    return KTO_ODDAJE

async def kto(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['kto'] = update.message.text
    await update.message.reply_text("Komu oddajesz zmianę?")
    return KOMU

async def komu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['komu'] = update.message.text
    data = context.user_data

    msg = (
        f"📝 Nowe zgłoszenie:\n\n"
        f"📅 Dzień: {data['dzien']}\n"
        f"⏰ Zmiana: {data['zmiana']}\n"
        f"👤 Oddaje: {data['kto']}\n"
        f"➡️ Komu: {data['komu']}"
    )

    # Wyślij Tobie (adminowi)
    await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=msg)
    await update.message.reply_text("Dziękujemy! Zgłoszenie wysłane.")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Anulowano formularz.")
    return ConversationHandler.END

def main():
    # Wklej swój token poniżej:
    app = ApplicationBuilder().token("8087667975:AAFf3ZrcV4SRD-nMTeldU-a2bw5Ee__CxHQ").build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            DZIEŃ: [MessageHandler(filters.TEXT & ~filters.COMMAND, dzien)],
            ZMIANA: [MessageHandler(filters.TEXT & ~filters.COMMAND, zmiana)],
            KTO_ODDAJE: [MessageHandler(filters.TEXT & ~filters.COMMAND, kto)],
            KOMU: [MessageHandler(filters.TEXT & ~filters.COMMAND, komu)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv)
    app.run_polling()

if __name__ == '__main__':
    main()
