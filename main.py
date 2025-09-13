    # main.py
import os
import time
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ---------- Change these only for quick testing ----------
# Prefer environment variable TG_BOT_TOKEN, otherwise fallback to hardcoded (for now)
BOT_TOKEN = os.environ.get("TG_BOT_TOKEN") or "8334907704:AAGUtA4tJWIwSPmrD_X2XfzY9wC59RTeu-w"
# Prefer env TG_GROUP_ID, otherwise fallback:
GROUP_CHAT_ID = int(os.environ.get("TG_GROUP_ID") or "-1002940360646")
# --------------------------------------------------------

def mask_token(tok: str) -> str:
    if not tok:
        return "<NONE>"
    if len(tok) <= 12:
        return tok
    return tok[:6] + "..." + tok[-6:]

print("=== Starting Telegram Bot ===")
print("DEBUG BOT_TOKEN:", mask_token(BOT_TOKEN))
print("DEBUG GROUP_CHAT_ID:", GROUP_CHAT_ID)

if not BOT_TOKEN:
    print("ERROR: BOT token missing. Set TG_BOT_TOKEN environment variable or hardcode it in main.py")
    # keep the process alive so Render doesn't just crash silently
    while True:
        time.sleep(60)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    fullname = f"{user.first_name or ''} {user.last_name or ''}".strip()
    username = f"@{user.username}" if user.username else "(no username)"
    text = (
        f"📢 New user started the bot!\n\n"
        f"👤 Name: {fullname}\n"
        f"🔗 Username: {username}\n"
        f"🆔 User ID: {user.id}"
    )

    try:
        await context.bot.send_message(chat_id=GROUP_CHAT_ID, text=text)
        await update.message.reply_text("✅ Aapki info group/channel mein bhej di gayi hai.")
    except Exception as e:
        # Inform user if sending to channel/group failed (useful for debugging)
        await update.message.reply_text(f"❌ Group send failed: {e}")

def main():
    # Build the application (will raise if token is invalid)
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    print("Bot is running. Waiting for /start ...")
    app.run_polling()

if __name__ == "__main__":
    main()
    
    
