from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardRemove,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

# -------------- STAŁE -----------------
DZIEŃ, ZMIANA, KTO_ODDAJE, KOMU = range(4)

GROUP_CHAT_ID = -1002360593885      # ID Twojej grupy
GROUP_THREAD_ID = 4962              # ID wątku w grupie

# -------------- START -----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Poniedziałek", callback_data="Poniedziałek"),
            InlineKeyboardButton("Wtorek",       callback_data="Wtorek"),
            InlineKeyboardButton("Środa",        callback_data="Środa"),
        ],
        [
            InlineKeyboardButton("Czwartek", callback_data="Czwartek"),
            InlineKeyboardButton("Piątek",   callback_data="Piątek"),
            InlineKeyboardButton("Sobota",   callback_data="Sobota"),
        ],
        [
            InlineKeyboardButton("Niedziela", callback_data="Niedziela"),
        ],
    ])

    msg = await update.message.reply_text(
        "🗓 Wybierz dzień zamiany:", reply_markup=keyboard
    )

    # lista wiadomości do późniejszego usunięcia
    context.user_data["to_delete"] = [msg.message_id]
    return DZIEŃ

# -------------- DZIEŃ -----------------
async def dzien_cb(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    context.user_data["dzien"] = query.data
    await query.message.delete()                     # usuwamy kafelki

    msg = await query.message.reply_text(
        "🕐 Podaj zmianę:", reply_markup=ReplyKeyboardRemove()
    )
    context.user_data["to_delete"].append(msg.message_id)
    return ZMIANA

# -------------- ZMIANA ----------------
async def zmiana(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["zmiana"] = update.message.text
    context.user_data["to_delete"].append(update.message.message_id)

    msg = await update.message.reply_text("👤 Kto oddaje zmianę?")
    context.user_data["to_delete"].append(msg.message_id)
    return KTO_ODDAJE

# -------------- KTO_ODDAJE -----------
async def kto(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["kto"] = update.message.text
    context.user_data["to_delete"].append(update.message.message_id)

    msg = await update.message.reply_text("➡️ Komu oddajesz zmianę?")
    context.user_data["to_delete"].append(msg.message_id)
    return KOMU

# -------------- KOMU -----------------
async def komu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["komu"] = update.message.text
    context.user_data["to_delete"].append(update.message.message_id)

    data = context.user_data
    zgłoszenie = (
        f"📝 **Nowe zgłoszenie zamiany**:\n\n"
        f"📅 Dzień: {data['dzien']}\n"
        f"⏰ Zmiana: {data['zmiana']}\n"
        f"👤 Oddaje: {data['kto']}\n"
        f"➡️ Komu: {data['komu']}"
    )

    # wysyłamy do wątku w grupie
    await context.bot.send_message(
        chat_id=GROUP_CHAT_ID,
        message_thread_id=GROUP_THREAD_ID,
        text=zgłoszenie,
        parse_mode="Markdown",
    )

    potwierdzenie = await update.message.reply_text(
        "✅ Dziękujemy! Zgłoszenie zostało wysłane."
    )
    context.user_data["to_delete"].append(potwierdzenie.message_id)

    # kasujemy wszystkie wcześniejsze wiadomości
    for mid in context.user_data.get("to_delete", []):
        try:
            await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=mid)
        except Exception:
            # brak uprawnień / wiadomość za stara – pomijamy
            pass

    return ConversationHandler.END

# -------------- CANCEL ---------------
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # usuwamy zostawione wcześniej wiadomości
    for mid in context.user_data.get("to_delete", []):
        try:
            await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=mid)
        except Exception:
            pass

    await update.message.reply_text(
        "❌ Formularz został anulowany.", reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

# -------------- MAIN -----------------
def main() -> None:
    # PRZYPOMINAM: trzymaj token w bezpiecznym miejscu (np. zmienna środowiskowa)
    app = ApplicationBuilder().token("8087667975:AAFf3ZrcV4SRD-nMTeldU-a2bw5Ee__CxHQ").build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            DZIEŃ:   [CallbackQueryHandler(dzien_cb)],
            ZMIANA:  [MessageHandler(filters.TEXT & ~filters.COMMAND, zmiana)],
            KTO_ODDAJE: [MessageHandler(filters.TEXT & ~filters.COMMAND, kto)],
            KOMU:    [MessageHandler(filters.TEXT & ~filters.COMMAND, komu)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
