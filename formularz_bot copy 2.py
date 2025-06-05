from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

# Etapy formularza
DZIEŃ, ZMIANA, KTO_ODDAJE, KOMU = range(4)

# ID grupy i wątku
GROUP_CHAT_ID = -1002360593885
GROUP_THREAD_ID = 4962

DNI = [
    ["Poniedziałek", "Wtorek", "Środa"],
    ["Czwartek", "Piątek", "Sobota"],
    ["Niedziela"]
]

# START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(day, callback_data=day) for day in row]
        for row in DNI
    ])
    msg = await update.message.reply_text(
        "🕛 Wybierz dzień zamiany:", reply_markup=keyboard
    )
    context.user_data['to_delete'] = [update.message.message_id, msg.message_id]
    return DZIEŃ

# WYBÓR DNIA (inline buttons)
async def dzien_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    context.user_data['dzien'] = query.data

    msg = await query.message.reply_text(
        "🕐 Podaj zmianę:", reply_markup=ReplyKeyboardRemove()
    )
    context.user_data['to_delete'].append(msg.message_id)
    return ZMIANA

async def zmiana(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['zmiana'] = update.message.text
    msg = await update.message.reply_text(" 👤 Kto oddaje zmianę?")
    context.user_data['to_delete'].append(update.message.message_id)
    context.user_data['to_delete'].append(msg.message_id)
    return KTO_ODDAJE

async def kto(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['kto'] = update.message.text
    msg = await update.message.reply_text(" ➡️ Komu oddajesz zmianę?")
    context.user_data['to_delete'].append(update.message.message_id)
    context.user_data['to_delete'].append(msg.message_id)
    return KOMU

async def komu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['komu'] = update.message.text
    context.user_data['to_delete'].append(update.message.message_id)
    data = context.user_data

    msg = (
    f"📍 **Nowe zgłoszenie zamiany**:\n"
    f"📅 Dzień: {data['dzien']}\n"
    f"⏰ Zmiana: {data['zmiana']}\n"
    f"👤 Oddaje: {data['kto']}\n"
    f"➡️ Komu: {data['komu']}"
)

    await context.bot.send_message(
        chat_id=GROUP_CHAT_ID,
        message_thread_id=GROUP_THREAD_ID,
        text=msg,
        parse_mode="Markdown"
    )

    confirm = await update.message.reply_text(
        "✅ Dziękujemy! Zgłoszenie zostało wysłane."
    )
    context.user_data['to_delete'].append(confirm.message_id)

    # Usuwanie wszystkich wiadomosci użytkownika i bota po zakończeniu
    for msg_id in context.user_data['to_delete']:
        try:
            await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=msg_id)
        except:
            pass  # np. za stare lub nie masz uprawnień

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "❌ Formularz anulowany.", reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

def main():
    app = ApplicationBuilder().token("<8087667975:AAFf3ZrcV4SRD-nMTeldU-a2bw5Ee__CxHQN>").build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            DZIEŃ: [CallbackQueryHandler(dzien_callback)],
            ZMIANA: [MessageHandler(filters.TEXT & ~filters.COMMAND, zmiana)],
            KTO_ODDAJE: [MessageHandler(filters.TEXT & ~filters.COMMAND, kto)],
            KOMU: [MessageHandler(filters.TEXT & ~filters.COMMAND, komu)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        per_message=True,
    )

    app.add_handler(conv_handler)
    app.run_polling()

if __name__ == '__main__':
    main()
