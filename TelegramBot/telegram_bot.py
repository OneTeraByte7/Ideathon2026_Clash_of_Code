from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, ContextTypes

from telegram_service import BOT_TOKEN, CHAT_ID

# 🔥 Handle button clicks
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    patient_id = data.split("_",1)[1] if "_" in data else None

    # safe answer, ignore old callback errors
    try:
        await query.answer()
    except Exception as e:
        print("⚠️ callback-answer err:", e)

    if data.startswith("approve"):
        text = f"✅ Doctor APPROVED the treatment for patient {patient_id}."

    elif data.startswith("reject"):
        text = (
            f"❌ Doctor REJECTED the treatment for patient {patient_id}.\n"
            "Please send a note with /note <patient_id> <your note>"
        )

    elif data.startswith("modify"):
        text = (
            f"✏️ Doctor wants to MODIFY the treatment for patient {patient_id}.\n"
            "Please send a note with /note <patient_id> <your note>"
        )

    else:
        text = "⚠️ Unknown action"

    # optionally edit message text (and this can also fail if old)
    try:
        await query.edit_message_text(text=text)
    except Exception as e:
        print("⚠️ callback-edit err:", e)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=text)


# 📝 /note command for additional doctor comments
async def note_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text or ""
    parts = text.split(" ", 2)

    if len(parts) < 3:
        await update.message.reply_text("Usage: /note <patient_id> <your note>")
        return

    patient_id, note = parts[1], parts[2]
    reply = f"📝 Note received for patient {patient_id}: {note}"

    # This message can be relayed elsewhere (DB, doctor channel, etc.)
    # For now we echo to the current chat and send a follow-up to the doctor chat.
    await update.message.reply_text(reply)
    await context.bot.send_message(chat_id=CHAT_ID, text=f"🩺 Doctor note for {patient_id}: {note}")


# � Error reporting
async def error_handler(update, context):
    print("❌ Bot error:", context.error)


# �🚀 Start bot
def start_bot():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(CommandHandler("note", note_handler))

    app.add_error_handler(error_handler)

    print("🤖 Telegram Bot Running...")
    app.run_polling()


if __name__ == "__main__":
    start_bot()