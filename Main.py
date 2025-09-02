import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ChatMemberHandler,
    ContextTypes,
    filters,
)
from telegram.constants import ChatMemberStatus

# ================== CONFIG ==================
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_USERNAME = "@redhu321"
LOGGER_GROUP_ID = -1002724746525

# Global start message
START_MESSAGE = """😎 Welcome to NSFW Protection Bot! 🏞️  
I’m an AI☔-powered guardian built to keep your Telegram groups safe, clean, and spam-free.

🚀 What I do:  
🛡️ Block NSFW Stickers & Media 🔞  
⚠️ Warn & Ban System (5 warnings → ban)  
⚡ Always Active 🛜 (24/7 protection)

✨ Add➕ me to your group today and let’s make Telegram safer!  

👑 Owner: {owner}  
📢 Updates & Support: https://t.me/hert_beat_fm_update
""".format(owner=OWNER_USERNAME)

# ============================================

# Sticker warning tracker
user_sticker_warnings = {}

# ============== Sticker Checking ============
async def check_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not user:
        return

    user_id = user.id
    count = user_sticker_warnings.get(user_id, 0) + 1
    user_sticker_warnings[user_id] = count

    # Delete sticker
    try:
        await update.message.delete()
    except Exception:
        pass

    if count >= 5:
        try:
            await update.effective_chat.ban_member(user_id)
            await context.bot.send_message(
                update.effective_chat.id,
                f"🚫 {user.mention_html()} was banned for repeated NSFW stickers.",
                parse_mode="HTML",
            )
        except Exception:
            pass
    else:
        await update.message.reply_text(
            f"{user.mention_html()} warning {count}/5 for stickers.",
            parse_mode="HTML",
        )

# ============== Logger for Bot Status ============
async def track_bot_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = update.my_chat_member
    chat = update.effective_chat
    status = result.new_chat_member.status

    if status == ChatMemberStatus.MEMBER:  # Bot added
        await context.bot.send_message(
            LOGGER_GROUP_ID,
            f"✅ Bot added to group:\n<b>{chat.title}</b>\n🆔 ID: {chat.id}",
            parse_mode="HTML",
        )

    elif status in [ChatMemberStatus.KICKED, ChatMemberStatus.LEFT]:  # Bot removed
        await context.bot.send_message(
            LOGGER_GROUP_ID,
            f"❌ Bot removed from group:\n<b>{chat.title}</b>\n🆔 ID: {chat.id}",
            parse_mode="HTML",
        )

# ============== Start Command ============
async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.chat.type == "private":
        keyboard = [
            [
                InlineKeyboardButton("➕ Add Me", url="https://t.me/Scanner_ro_bot?startgroup=s&admin=delete_messages+ban_users"),
            ],
            [
                InlineKeyboardButton("👑 Owner", url="https://t.me/redhu321"),
                InlineKeyboardButton("📢 Updates", url="https://t.me/hert_beat_fm_update"),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(START_MESSAGE, reply_markup=reply_markup)

# ============== MAIN ================
if __name__ == "__main__":
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(MessageHandler(filters.Sticker.ALL, check_sticker))
    app.add_handler(ChatMemberHandler(track_bot_status, ChatMemberHandler.MY_CHAT_MEMBER))

    print("🤖 Bot is running...")
    app.run_polling()
