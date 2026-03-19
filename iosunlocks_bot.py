"""
iosunlocks Telegram Group Bot
================================
FIXED VERSION — Compatible with Python 3.14+
Install: pip install "python-telegram-bot[job-queue]==21.5"
Run:     python iosunlocks_bot.py
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ChatMemberHandler,
    filters,
    ContextTypes,
)

# ============================================================
#                        CONFIG
# ============================================================

BOT_TOKEN      = "8667357736:AAGnoC1eLb8nYmXWnzlsn95rma9YMkvEVVo"
ADMIN_LINK     = "https://t.me/official_apple_server"
CHANNEL_LINK   = "https://t.me/officialappleunlocking"
WEBSITE_LINK   = "https://www.iosunlocks.com"
WHATSAPP_LINK  = "https://wa.me/12672021860"

# ============================================================
#               WELCOME MESSAGE (shown when user joins)
# ============================================================

def build_welcome_message(first_name: str) -> str:
    return (
        f"👋 Welcome, {first_name}!\n\n"
        f"🔓 You've just joined the #1 iOS Unlocking Service.\n\n"
        f"Here's what we offer:\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📱 Permanent iCloud Unlock — All iPhone models\n"
        f"📡 Permanent Network Unlock — Any carrier, any country\n"
        f"⌚ Apple Watch Unlock — All series\n"
        f"💻 MacBook Unlock — iCloud & Firmware\n"
        f"━━━━━━━━━━━━━━━━━━\n\n"
        f"✅ Fast — Results within 24 hours\n"
        f"✅ Permanent — Never locks again\n"
        f"✅ Remote — 100% online, worldwide\n"
        f"✅ Trusted — 1,000+ devices unlocked\n\n"
        f"👇 Use the buttons below to get started:"
    )

# ============================================================
#         REPLY MESSAGE (shown when user types anything)
# ============================================================

def build_reply_message(first_name: str) -> str:
    return (
        f"👋 Hi {first_name}!\n\n"
        f"⚡ Our team is available 24/7 — we reply within minutes.\n\n"
        f"👇 Choose an option below to reach us:"
    )

# ============================================================
#                        BUTTONS
# ============================================================

def get_main_buttons() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("👨‍💼 Contact Admin",       url=ADMIN_LINK)],
        [InlineKeyboardButton("📢 Join Our Channel",     url=CHANNEL_LINK)],
        [InlineKeyboardButton("🌐 Visit Website",        url=WEBSITE_LINK)],
        [InlineKeyboardButton("💬 Message on WhatsApp",  url=WHATSAPP_LINK)],
    ]
    return InlineKeyboardMarkup(keyboard)

# ============================================================
#          WELCOME HANDLER — fires when a user joins
# ============================================================

async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = update.chat_member

    # Only trigger on new joins
    old_status = result.old_chat_member.status
    new_status = result.new_chat_member.status

    joined = (
        old_status in ["left", "kicked", "restricted"]
        and new_status in ["member", "administrator", "creator"]
    )

    if not joined:
        return

    new_user = result.new_chat_member.user
    if new_user.is_bot:
        return

    first_name = new_user.first_name or "Friend"

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=build_welcome_message(first_name),
        reply_markup=get_main_buttons(),
    )

# ============================================================
#       MESSAGE HANDLER — fires when user sends a message
# ============================================================

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.effective_user:
        return

    user = update.effective_user
    if user.is_bot:
        return

    first_name = user.first_name or "Friend"

    await update.message.reply_text(
        text=build_reply_message(first_name),
        reply_markup=get_main_buttons(),
    )

# ============================================================
#                   /start COMMAND
# ============================================================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    first_name = user.first_name if user else "Friend"

    await update.message.reply_text(
        text=build_welcome_message(first_name),
        reply_markup=get_main_buttons(),
    )

# ============================================================
#                        MAIN
# ============================================================

def main():
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("  🤖 iosunlocks Bot is starting...")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("✅ Bot is running! Press CTRL+C to stop.\n")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(ChatMemberHandler(welcome_new_member, ChatMemberHandler.CHAT_MEMBER))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
