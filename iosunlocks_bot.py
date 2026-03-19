"""
iosunlocks Telegram Group Bot — FULL VERSION WITH LOCAL VIDEO
=============================================================
Install: pip install "python-telegram-bot[job-queue]==21.5" httpx==0.27.0
Run:     python iosunlocks_bot.py

IMPORTANT: Put your video file "IMG_4956.MP4" in the SAME folder as this script.
"""

import os
import re
import httpx
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
ADMIN_LINK     = "https://t.me/networks_iclouds_unlocks"
CHANNEL_LINK   = "https://t.me/officialappleunlocking"
WEBSITE_LINK   = "https://www.iosunlocks.com"
WHATSAPP_LINK  = "https://wa.me/12672021860"

# ============================================================
#   LOCAL VIDEO FILE
#   Make sure IMG_4956.MP4 is in the same folder as this script
# ============================================================

VIDEO_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "IMG_4956.MP4")

# This stores the Telegram file_id after first upload
# so the video is only uploaded once and reused after that
_cached_file_id = None

# ============================================================
#               WELCOME MESSAGE
# ============================================================

def build_welcome_message(first_name: str) -> str:
    return (
        f"🎉 Welcome {first_name} To iOS Unlocking Services.\n\n"
        f"✅ FOR ANY UNLOCK SERVICE CONTACT WEBOWNER\n\n"
        f"✅ GROUP RULES /rules\n"
        f"✅ STAFF /staff\n\n"
        f"✏️ Auto Pay accepted on web\n\n"
        f"❌ note 📋 : work with only admins to avoid been scammed.\n\n"
        f"☑️ /check — Check FMI ON/OFF by IMEI ☑️\n\n"
        f"Example — /check 356200549868335"
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
        [
            InlineKeyboardButton("🌐 Website", url=WEBSITE_LINK)
        ],
        [
            InlineKeyboardButton("👨‍💼 Owner",   url=ADMIN_LINK),
            InlineKeyboardButton("🔔 Updates",  url=CHANNEL_LINK),
        ],
        [
            InlineKeyboardButton("💬 WhatsApp", url=WHATSAPP_LINK)
        ],
    ]
    return InlineKeyboardMarkup(keyboard)

# ============================================================
#         SEND WELCOME VIDEO — uploads once, reuses after
# ============================================================

async def send_welcome_video(chat_id, caption, context, reply_to=None):
    global _cached_file_id

    try:
        if _cached_file_id:
            # Reuse already-uploaded file (faster)
            msg = await context.bot.send_animation(
                chat_id=chat_id,
                animation=_cached_file_id,
                caption=caption,
                reply_markup=get_main_buttons(),
                reply_to_message_id=reply_to,
            )
        else:
            # First time — upload the local file
            with open(VIDEO_FILE, "rb") as video:
                msg = await context.bot.send_animation(
                    chat_id=chat_id,
                    animation=video,
                    caption=caption,
                    reply_markup=get_main_buttons(),
                    reply_to_message_id=reply_to,
                )
            # Cache the file_id for next time
            if msg.animation:
                _cached_file_id = msg.animation.file_id
                print(f"✅ Video uploaded to Telegram. file_id cached.")

    except FileNotFoundError:
        print(f"❌ ERROR: Could not find {VIDEO_FILE}")
        print("Make sure IMG_4956.MP4 is in the same folder as this script.")
        # Fallback — send text only
        await context.bot.send_message(
            chat_id=chat_id,
            text=caption,
            reply_markup=get_main_buttons(),
        )
    except Exception as e:
        print(f"❌ Video send error: {e}")
        # Fallback — send text only
        await context.bot.send_message(
            chat_id=chat_id,
            text=caption,
            reply_markup=get_main_buttons(),
        )

# ============================================================
#       WELCOME HANDLER — fires when a new user joins
# ============================================================

async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = update.chat_member

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

    await send_welcome_video(
        chat_id=update.effective_chat.id,
        caption=build_welcome_message(first_name),
        context=context,
    )

# ============================================================
#     MESSAGE HANDLER — fires when user types anything
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
#       /check COMMAND — Check FMI ON/OFF by IMEI
# ============================================================

async def check_fmi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "❌ Please provide an IMEI number.\n\n"
            "Example: /check 356200549868335"
        )
        return

    imei = context.args[0].strip()

    if not re.fullmatch(r"\d{15}", imei):
        await update.message.reply_text(
            "❌ Invalid IMEI. Must be exactly 15 digits.\n\n"
            "Example: /check 356200549868335"
        )
        return

    await update.message.reply_text(f"🔍 Checking IMEI: {imei}...\nPlease wait.")

    try:
        url = f"https://imeicheck.net/api/check?imei={imei}&service=1"
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.get(url)
            data = response.json()

        if data.get("status") == "success":
            fmi = data.get("properties", {}).get("findMyIphone", "Unknown")
            device = data.get("properties", {}).get("deviceName", "Unknown Device")
            model = data.get("properties", {}).get("modelName", "")
            fmi_status = "🔴 ON (iCloud Locked)" if str(fmi).lower() in ["true", "on", "1", "yes"] else "🟢 OFF (Clean)"

            await update.message.reply_text(
                f"📱 IMEI Check Result\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"IMEI: {imei}\n"
                f"Device: {device} {model}\n"
                f"FMI Status: {fmi_status}\n"
                f"━━━━━━━━━━━━━━━━━━\n\n"
                f"Need an unlock? Contact us below 👇",
                reply_markup=get_main_buttons(),
            )
        else:
            raise ValueError("No result")

    except Exception:
        await update.message.reply_text(
            f"📱 IMEI: {imei}\n\n"
            f"⚠️ Could not fetch FMI status automatically.\n"
            f"Please contact our admin for a manual check 👇",
            reply_markup=get_main_buttons(),
        )

# ============================================================
#       /rules COMMAND
# ============================================================

async def rules_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📋 GROUP RULES\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "1️⃣ No spamming or flooding the group.\n"
        "2️⃣ Only deal with verified admins.\n"
        "3️⃣ No scamming — offenders will be banned.\n"
        "4️⃣ Be respectful to all members.\n"
        "5️⃣ No sharing of personal information.\n"
        "6️⃣ All unlock requests go through admin only.\n"
        "7️⃣ Auto Pay is accepted on our website only.\n\n"
        "❌ Violating rules = instant ban.\n\n"
        "Stay safe — only work with admins! 👇",
        reply_markup=get_main_buttons(),
    )

# ============================================================
#       /staff COMMAND
# ============================================================

async def staff_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👥 OFFICIAL STAFF\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "👨‍💼 Owner / Admin:\n"
        "@networks_iclouds_unlocks\n\n"
        "🌐 Website:\n"
        "www.iosunlocks.com\n\n"
        "💬 WhatsApp:\n"
        "+1 267 202 1860\n\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "⚠️ Only deal with the above official accounts.\n"
        "Anyone else claiming to be staff is a SCAMMER. 👇",
        reply_markup=get_main_buttons(),
    )

# ============================================================
#       /start COMMAND
# ============================================================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    first_name = user.first_name if user else "Friend"

    await send_welcome_video(
        chat_id=update.effective_chat.id,
        caption=build_welcome_message(first_name),
        context=context,
    )

# ============================================================
#                        MAIN
# ============================================================

def main():
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("  🤖 iosunlocks Bot is starting...")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    if os.path.exists(VIDEO_FILE):
        print(f"✅ Video file found: {VIDEO_FILE}")
    else:
        print(f"⚠️  WARNING: Video file NOT found at {VIDEO_FILE}")
        print("   Place IMG_4956.MP4 in the same folder as this script!")

    print("✅ Bot is running! Press CTRL+C to stop.\n")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("rules", rules_command))
    app.add_handler(CommandHandler("staff", staff_command))
    app.add_handler(CommandHandler("check", check_fmi))

    app.add_handler(ChatMemberHandler(welcome_new_member, ChatMemberHandler.CHAT_MEMBER))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
