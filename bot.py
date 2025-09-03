import asyncio
import threading
import sqlite3
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# ================== CONFIG ==================
BOT_TOKEN = "8334907704:AAGUtA4tJWIwSPmrD_X2XfzY9wC59RTeu-w"
CHANNELS = ["@muqeetcanvaproofs", "@proofssent", "@muqeetcanvaofficial"]
ADMIN_GROUP = -1002940360646
DB_FILE = "bot.db"
# ============================================

# Flask app (Render needs port open)
app = Flask(__name__)

@app.route("/")
def home():
    return "🤖 Bot is running fine!"

# ============= DATABASE SETUP =============
conn = sqlite3.connect(DB_FILE, check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    points INTEGER DEFAULT 0,
    referrals INTEGER DEFAULT 0
)""")
conn.commit()

def add_user(user_id):
    cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
    conn.commit()

def update_points(user_id, points):
    cursor.execute("UPDATE users SET points = points + ? WHERE user_id = ?", (points, user_id))
    conn.commit()

def get_points(user_id):
    cursor.execute("SELECT points FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    return row[0] if row else 0
# ===========================================

# ============= TELEGRAM BOT CODE =============
async def is_subscribed(app, user_id):
    for channel in CHANNELS:
        try:
            member = await app.bot.get_chat_member(chat_id=channel, user_id=user_id)
            if member.status in ["left", "kicked"]:
                return False
        except:
            return False
    return True

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    add_user(user_id)

    if not await is_subscribed(context.application, user_id):
        buttons = [
            [InlineKeyboardButton(f"Join {ch}", url=f"https://t.me/{ch.replace('@','')}")]
            for ch in CHANNELS
        ]
        buttons.append([InlineKeyboardButton("✅ Check Again", callback_data="check")])
        reply_markup = InlineKeyboardMarkup(buttons)
        await update.message.reply_text(
            "⚠️ You must join all the channels below to continue:",
            reply_markup=reply_markup
        )
    else:
        menu_buttons = [
            [InlineKeyboardButton("👥 Invite Friends", callback_data="invite")],
            [InlineKeyboardButton("🎁 Withdraw", callback_data="withdraw")],
            [InlineKeyboardButton("📊 My Points", callback_data="points")]
        ]
        await update.message.reply_text("✅ Welcome to the Main Menu:", reply_markup=InlineKeyboardMarkup(menu_buttons))

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    username = query.from_user.username or "No Username"

    if query.data == "check":
        if not await is_subscribed(context.application, user_id):
            await query.edit_message_text("❌ You have not joined all channels yet.")
        else:
            menu_buttons = [
                [InlineKeyboardButton("👥 Invite Friends", callback_data="invite")],
                [InlineKeyboardButton("🎁 Withdraw", callback_data="withdraw")],
                [InlineKeyboardButton("📊 My Points", callback_data="points")]
            ]
            await query.edit_message_text("✅ Thank you! You have joined all channels.", reply_markup=InlineKeyboardMarkup(menu_buttons))

    elif query.data == "invite":
        referral_link = f"https://t.me/{context.application.bot.username}?start={user_id}"
        await query.message.reply_text(f"👥 Invite your friends using this link:\n{referral_link}\n\nYou earn 2 points for each referral!")

    elif query.data == "points":
        points = get_points(user_id)
        await query.message.reply_text(f"📊 Your Current Balance: {points} Points")

    elif query.data == "withdraw":
        buttons = [
            [InlineKeyboardButton("✅ Yes", callback_data="confirm_withdraw")],
            [InlineKeyboardButton("❌ No", callback_data="cancel_withdraw")]
        ]
        await query.message.reply_text("⚠️ Confirm Your Withdrawal", reply_markup=InlineKeyboardMarkup(buttons))

    elif query.data == "cancel_withdraw":
        await query.message.reply_text("❌ Withdrawal Cancelled.")

    elif query.data == "confirm_withdraw":
        points = get_points(user_id)
        if points < 20:
            await query.message.reply_text("⚠️ You need at least 20 Points to withdraw.")
        else:
            update_points(user_id, -20)
            msg = (
                "🆕 New CANVA PRO PURCHASED 🎉\n\n"
                f"👤 User: @{username}\n"
                f"🆔 ID: {user_id}\n"
                f"🛒 Bought: CANVA PRO\n"
                f"💵 Price: 20 Points"
            )
            await context.bot.send_message(chat_id=ADMIN_GROUP, text=msg)
            await query.message.reply_text("✅ Your Withdrawal Request has been sent to Admin. Please wait.")

# ============= RUN BOT =============
async def main():
    tg_app = Application.builder().token(BOT_TOKEN).build()
    tg_app.add_handler(CommandHandler("start", start))
    tg_app.add_handler(CallbackQueryHandler(button))

    # Start Flask in a separate thread
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=5000)).start()

    # Start Telegram Bot in main thread
    await tg_app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
                               
