# formularz_bot.py
"""
Bot Telegram – zgłaszanie zamian dyżurów.

• Przyciski inline do wyboru dnia.
• Obsługa wątków (forum topics): kolejne wiadomości trafiają do tego samego
  wątku, z którego wystartowano /start.
• Po zakończeniu rozmowy bot kasuje swoje i użytkownika wiadomości.
"""

from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
)
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ConversationHandler,
    CallbackQueryHandler, MessageHandler, ContextTypes, filters
)
from telegram.error import BadRequest

# ---------- KONST ---------
DZIEŃ, ZMIANA, KTO_ODDAJE, KOMU = range(4)

GROUP_CHAT_ID   = -1002360593885   # ID grupy
GROUP_THREAD_ID = 4962             # ID wątku “TEST”, do którego trafia gotowe zgłoszenie

# ---------- POMOCNICZE ----
async def _send_and_track(
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: int,
    thread_id: int | None,
    text: str,
    to_delete: list[int],
    reply_markup=None,
):
    """Wyślij wiadomość w dany czat/wątek i zapisz id do sprzątania."""
    msg = await context.bot.send_message(
        chat_id=chat_id,
        message_thread_id=thread_id,
        text=text,
        reply_markup=reply_markup,
    )
    to_delete.append(msg.message_id)
    return msg


# ---------- HANDLERY ------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Początek rozmowy – przyciski z dniami tygodnia."""
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(d, callback_data=d) for d in ("Poniedziałek", "Wtorek", "Środa")],
        [InlineKeyboardButton(d, callback_data=d) for d in ("Czwartek", "Piątek", "Sobota")],
        [InlineKeyboardButton("Niedziela", callback_data="Niedziela")],
    ])

    # zapisz identyfikatory czatu i wątku, w którym uruchomiono /start
    context.user_data["chat_id"]   = update.effective_chat.id
    context.user_data["thread_id"] = update.message.message_thread_id    # None poza forum
    context.user_data["to_delete"] = []

    msg = await update.message.reply_text("🗓 Wybierz dzień zamiany:", reply_markup=keyboard)
    context.user_data["to_delete"].append(msg.message_id)
    return DZIEŃ


async def dzien_cb(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Kliknięto kafelek z dniem."""
    q = update.callback_query
    await q.answer()
    context.user_data["dzien"] = q.data

    # stary kafelek zostawiamy do sprzątania ‑ skasujemy go od razu, jeśli się uda
    try:
        await q.message.delete()
    except BadRequest:
        context.user_data["to_delete"].append(q.message.message_id)

    await _send_and_track(
        context,
        chat_id=context.user_data["chat_id"],
        thread_id=context.user_data["thread_id"],
        text="🕐 Podaj zmianę:",
        reply_markup=ReplyKeyboardRemove(),
        to_delete=context.user_data["to_delete"],
    )
    return ZMIANA


async def zmiana(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["zmiana"] = update.message.text
    context.user_data["to_delete"].append(update.message.message_id)

    await _send_and_track(
        context,
        context.user_data["chat_id"],
        context.user_data["thread_id"],
        "👤 Kto oddaje zmianę?",
        context.user_data["to_delete"],
    )
    return KTO_ODDAJE


async def kto(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["kto"] = update.message.text
    context.user_data["to_delete"].append(update.message.message_id)

    await _send_and_track(
        context,
        context.user_data["chat_id"],
        context.user_data["thread_id"],
        "➡️ Komu oddajesz zmianę?",
        context.user_data["to_delete"],
    )
    return KOMU


async def komu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["komu"] = update.message.text
    context.user_data["to_delete"].append(update.message.message_id)

    d = context.user_data
    zgłoszenie = (
        f"📝 **Nowe zgłoszenie zamiany**:\n\n"
        f"📅 Dzień: {d['dzien']}\n"
        f"⏰ Zmiana: {d['zmiana']}\n"
        f"👤 Oddaje: {d['kto']}\n"
        f"➡️ Komu: {d['komu']}"
    )
    # wysyłka do wątku TEST w grupie
    await context.bot.send_message(
        chat_id=GROUP_CHAT_ID,
        message_thread_id=GROUP_THREAD_ID,
        text=zgłoszenie,
        parse_mode="Markdown",
    )

    await _send_and_track(
        context,
        context.user_data["chat_id"],
        context.user_data["thread_id"],
        "✅ Dziękujemy! Zgłoszenie zostało wysłane.",
        context.user_data["to_delete"],
    )

    # ---------- SPRZĄTANIE ----------
    for mid in context.user_data["to_delete"]:
        try:
            await context.bot.delete_message(context.user_data["chat_id"], mid)
        except BadRequest:
            pass

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    for mid in context.user_data.get("to_delete", []):
        try:
            await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=mid)
        except BadRequest:
            pass
    await update.message.reply_text("❌ Formularz został anulowany.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


# ---------- MAIN ------------
def main() -> None:
    import os

    # --- TOKEN ---
    TOKEN = os.getenv("BOT_TOKEN")          # export BOT_TOKEN="123:ABC..."
    TOKEN = "8087667975:AAFf3ZrcV4SRD-nMTeldU-a2bw5Ee__CxHQ"           # ← odkomentuj, jeżeli wolisz wpisać go na sztywno
    if not TOKEN:
        raise RuntimeError("Brak zmiennej środowiskowej BOT_TOKEN!")

    app = ApplicationBuilder().token(TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            DZIEŃ:       [CallbackQueryHandler(dzien_cb)],
            ZMIANA:      [MessageHandler(filters.TEXT & ~filters.COMMAND, zmiana)],
            KTO_ODDAJE:  [MessageHandler(filters.TEXT & ~filters.COMMAND, kto)],
            KOMU:        [MessageHandler(filters.TEXT & ~filters.COMMAND, komu)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv)
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
