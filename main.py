from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ---- Aapka Bot Token aur Group ID (hardcoded) ----
BOT_TOKEN = "8334907704:AAGUtA4tJWIwSPmrD_X2XfzY9wC59RTeu-w"
GROUP_CHAT_ID = -1002940360646  # Group/Channel ka ID

# ---- Start command handler ----
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    fullname = f"{user.first_name or ''} {user.last_name or ''}".strip()
    username = f"@{user.username}" if user.username else "(no username)"
    
    # Message for group
    text = (
        f"📢 New user started the bot!\n\n"
        f"👤 Name: {fullname}\n"
        f"🔗 Username: {username}\n"
        f"🆔 User ID: {user.id}"
    )
    
    # Send message to group
    await context.bot.send_message(chat_id=GROUP_CHAT_ID, text=text)
    
    # Reply to user
    await update.message.reply_text("✅ Aapki info group me send kar di gayi hai.")

# ---- Main function ----
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
    
