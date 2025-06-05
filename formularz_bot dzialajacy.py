from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
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

# Twoje ID grupy i wątku
GROUP_CHAT_ID = -1002360593885
GROUP_THREAD_ID = 4962

DNI_TYGODNIA = [
    ["Poniedziałek", "Wtorek", "Środa"],
    ["Czwartek", "Piątek", "Sobota"],
    ["Niedziela"]
]

# START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    keyboard = ReplyKeyboardMarkup(DNI_TYGODNIA, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("🗓 Wybierz dzień zamiany:", reply_markup=keyboard)
    return DZIEŃ

async def dzien(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['dzien'] = update.message.text
    await update.message.reply_text("🕐 Podaj zmianę:", reply_markup=ReplyKeyboardRemove())
    return ZMIANA

async def zmiana(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['zmiana'] = update.message.text
    await update.message.reply_text("👤 Kto oddaje zmianę?")
    return KTO_ODDAJE

async def kto(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['kto'] = update.message.text
    await update.message.reply_text("➡️ Komu oddajesz zmianę?")
    return KOMU

async def komu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['komu'] = update.message.text
    data = context.user_data

    msg = (
        f"📝 **Nowe zgłoszenie zamiany**:\n\n"
        f"📅 Dzień: {data['dzien']}\n"
        f"⏰ Zmiana: {data['zmiana']}\n"
        f"👤 Oddaje: {data['kto']}\n"
        f"➡️ Komu: {data['komu']}"
    )

    # Wysyłamy tylko do wątku TEST w grupie
    await context.bot.send_message(
        chat_id=GROUP_CHAT_ID,
        message_thread_id=GROUP_THREAD_ID,
        text=msg,
        parse_mode="Markdown"
    )

    await update.message.reply_text("✅ Dziękujemy! Zgłoszenie zostało wysłane.")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("❌ Formularz został anulowany.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

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
