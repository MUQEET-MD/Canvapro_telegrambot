# filename: bot_send_to_group.py
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import os

BOT_TOKEN = os.environ.get("8334907704:AAGUtA4tJWIwSPmrD_X2XfzY9wC59RTeu-w") or "YOUR_BOT_TOKEN_HERE"
# Replace with your group chat id (example: -1001234567890)
GROUP_CHAT_ID = int(os.environ.get("-1002940360646") or -1001234567890)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user is None:
        await update.message.reply_text("User info not found.")
        return

    # Prepare display name and username safely
    first = user.first_name or ""
    last = user.last_name or ""
    fullname = (first + " " + last).strip()
    username = f"@{user.username}" if user.username else "(no username)"

    # Message to send to the group
    text_for_group = f"New user started the bot:\nName: {fullname}\nUsername: {username}\nUser ID: {user.id}"

    # Send message to the group
    try:
        await context.bot.send_message(chat_id=GROUP_CHAT_ID, text=text_for_group)
    except Exception as e:
        # If sending fails, inform the user (and optionally log)
        await update.message.reply_text(f"Could not post to group. Error: {e}")
        return

    # Acknowledge to the user privately
    await update.message.reply_text("Thanks — your info was sent to the group.")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    print("Bot started. Press Ctrl+C to stop.")
    app.run_polling()

if __name__ == "__main__":
    main()
