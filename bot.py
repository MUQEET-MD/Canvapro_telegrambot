from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import sqlite3

# === BOT CONFIG ===
BOT_TOKEN = "YOUR_BOT_TOKEN"  # apna BotFather se liya token daalo
CHANNELS = ["@channel1", "@channel2", "@channel3"]  # force join channels
ADMIN_GROUP = -1001234567890  # apna withdrawal group ID

# === DATABASE ===
conn = sqlite3.connect("bot.db", check_same_thread=False)
cur = conn.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, points INTEGER DEFAULT 0, referrals INTEGER DEFAULT 0)")
conn.commit()


# --- Force Join Check ---
async def is_subscribed(app, user_id):
    for channel in CHANNELS:
        try:
            member = await app.bot.get_chat_member(chat_id=channel, user_id=user_id)
            if member.status in ["left", "kicked"]:
                return False
        except:
            return False
    return True


# --- Show Main Menu ---
async def show_main_menu(update: Update, text="🏠 Main Menu"):
    menu = InlineKeyboardMarkup([
        [InlineKeyboardButton("👥 Invite Users", callback_data="invite")],
        [InlineKeyboardButton("💰 Balance", callback_data="balance"),
         InlineKeyboardButton("💵 Withdraw", callback_data="withdraw")],
        [InlineKeyboardButton("📸 Proofs", callback_data="proofs"),
         InlineKeyboardButton("📞 Support", url="https://t.me/YourSupport")],
    ])

    if update.message:
        await update.message.reply_text(text, reply_markup=menu)
    else:
        await update.callback_query.edit_message_text(text, reply_markup=menu)


# --- Start Command ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    args = context.args

    # Add user to DB
    cur.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
    conn.commit()

    # Referral system
    if args:
        ref_id = int(args[0])
        if ref_id != user_id:
            cur.execute("UPDATE users SET points = points + 2, referrals = referrals + 1 WHERE user_id=?", (ref_id,))
            conn.commit()

    # Force join check
    if not await is_subscribed(context.application, user_id):
        buttons = [
            [InlineKeyboardButton(f"Join {ch}", url=f"https://t.me/{ch.replace('@','')}")]
            for ch in CHANNELS
        ]
        buttons.append([InlineKeyboardButton("✅ Check Again", callback_data="check")])
        reply_markup = InlineKeyboardMarkup(buttons)
        await update.message.reply_text(
            "⚠️ Aapko age barhne ke liye pehle in channels ko join karna hoga:",
            reply_markup=reply_markup
        )
    else:
        await show_main_menu(update)


# --- Callback Buttons ---
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    # Check Again
    if query.data == "check":
        if not await is_subscribed(context.application, user_id):
            await query.edit_message_text("❌ Aapne abhi tak sab channels join nahi kiye.")
        else:
            await show_main_menu(update)

    # Invite
    elif query.data == "invite":
        ref_link = f"https://t.me/{context.bot.username}?start={user_id}"
        await query.message.reply_text(f"🔗 Aapka referral link:\n{ref_link}\n\nHar ek referral pe aapko +2 points milenge!")

    # Balance
    elif query.data == "balance":
        cur.execute("SELECT points, referrals FROM users WHERE user_id=?", (user_id,))
        points, refs = cur.fetchone()
        await query.message.reply_text(f"💰 Balance: {points} Points\n👥 Referrals: {refs}")

    # Withdraw
    elif query.data == "withdraw":
        btns = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Yes", callback_data="yes_withdraw"),
             InlineKeyboardButton("❌ No", callback_data="no_withdraw")]
        ])
        await query.message.reply_text("⚠️ Confirm Your Withdrawal?", reply_markup=btns)

    elif query.data == "no_withdraw":
        await query.message.reply_text("❌ Withdrawal Cancelled.")
        await show_main_menu(update)

    elif query.data == "yes_withdraw":
        cur.execute("SELECT points FROM users WHERE user_id=?", (user_id,))
        points = cur.fetchone()[0]
        if points < 20:
            await query.message.reply_text("⚠️ Aapke paas withdrawal ke liye kam se kam 20 points hone chahiye.")
            return

        # Deduct points
        cur.execute("UPDATE users SET points = points - 20 WHERE user_id=?", (user_id,))
        conn.commit()

        # Send to Admin Group
        msg = f"""🆕 New CANVA PRO PURCHASED 🎉

👤 User:
🤵 Username: @{query.from_user.username or 'NoUsername'}
🆔 User ID: {user_id}
🛒 Bought: CANVA PRO
💵 Price: 20 Points
"""
        await context.bot.send_message(ADMIN_GROUP, msg)

        # Notify user
        await query.message.reply_text("✅ Your Withdrawal Request send to Admin.\nCheck Your Withdrawal @withdrawmassagegroup")

    elif query.data == "proofs":
        await query.message.reply_text("📸 Proofs section coming soon...")


# --- Main ---
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))

    print("🤖 Bot started...")
    app.run_polling()


if __name__ == "__main__":
    main()
