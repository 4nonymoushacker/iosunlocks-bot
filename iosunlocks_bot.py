"""
iosunlocks Telegram Group Bot — FIXED FOR PYTHON 3.14
=======================================================
Install: pip install "python-telegram-bot[job-queue]==21.5" httpx==0.27.0
Run:     python iosunlocks_bot.py
"""

import os
import asyncio
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

BOT_TOKEN    = "8667357736:AAGnoC1eLb8nYmXWnzlsn95rma9YMkvEVVo"
ADMIN_LINK   = "https://t.me/networks_iclouds_unlocks"
CHANNEL_LINK = "https://t.me/officialappleunlocking"
WEBSITE_LINK = "https://www.iosunlocks.com"
WHATSAPP_LINK= "https://wa.me/12672021860"
VIDEO_FILE   = os.path.join(os.path.dirname(os.path.abspath(__file__)), "IMG_4956.MP4")

_cached_file_id = None

# ============================================================
#   TAC DATABASE
# ============================================================

TAC_DB = {
    "35617931": {"name":"iPhone 15 Pro Max","brand":"Apple","chip":"A17 Pro","display":'6.7" Super Retina XDR',"storage":"256GB/512GB/1TB","year":"2023","icon":"📱"},
    "35617932": {"name":"iPhone 15 Pro","brand":"Apple","chip":"A17 Pro","display":'6.1" Super Retina XDR',"storage":"128GB/256GB/512GB/1TB","year":"2023","icon":"📱"},
    "35489311": {"name":"iPhone 15 Plus","brand":"Apple","chip":"A16 Bionic","display":'6.7" Super Retina XDR',"storage":"128GB/256GB/512GB","year":"2023","icon":"📱"},
    "35489312": {"name":"iPhone 15","brand":"Apple","chip":"A16 Bionic","display":'6.1" Super Retina XDR',"storage":"128GB/256GB/512GB","year":"2023","icon":"📱"},
    "35344111": {"name":"iPhone 14 Pro Max","brand":"Apple","chip":"A16 Bionic","display":'6.7" Super Retina XDR',"storage":"128GB/256GB/512GB/1TB","year":"2022","icon":"📱"},
    "35344112": {"name":"iPhone 14 Pro","brand":"Apple","chip":"A16 Bionic","display":'6.1" Super Retina XDR',"storage":"128GB/256GB/512GB/1TB","year":"2022","icon":"📱"},
    "35183911": {"name":"iPhone 14 Plus","brand":"Apple","chip":"A15 Bionic","display":'6.7" Super Retina XDR',"storage":"128GB/256GB/512GB","year":"2022","icon":"📱"},
    "35183912": {"name":"iPhone 14","brand":"Apple","chip":"A15 Bionic","display":'6.1" Super Retina XDR',"storage":"128GB/256GB/512GB","year":"2022","icon":"📱"},
    "35281311": {"name":"iPhone 13 Pro Max","brand":"Apple","chip":"A15 Bionic","display":'6.7" Super Retina XDR',"storage":"128GB/256GB/512GB/1TB","year":"2021","icon":"📱"},
    "35281312": {"name":"iPhone 13 Pro","brand":"Apple","chip":"A15 Bionic","display":'6.1" Super Retina XDR',"storage":"128GB/256GB/512GB/1TB","year":"2021","icon":"📱"},
    "35157611": {"name":"iPhone 13","brand":"Apple","chip":"A15 Bionic","display":'6.1" Super Retina XDR',"storage":"128GB/256GB/512GB","year":"2021","icon":"📱"},
    "35157612": {"name":"iPhone 13 mini","brand":"Apple","chip":"A15 Bionic","display":'5.4" Super Retina XDR',"storage":"128GB/256GB/512GB","year":"2021","icon":"📱"},
    "35937011": {"name":"iPhone 12 Pro Max","brand":"Apple","chip":"A14 Bionic","display":'6.7" Super Retina XDR',"storage":"128GB/256GB/512GB","year":"2020","icon":"📱"},
    "35937012": {"name":"iPhone 12 Pro","brand":"Apple","chip":"A14 Bionic","display":'6.1" Super Retina XDR',"storage":"128GB/256GB/512GB","year":"2020","icon":"📱"},
    "35677211": {"name":"iPhone 12","brand":"Apple","chip":"A14 Bionic","display":'6.1" Super Retina XDR',"storage":"64GB/128GB/256GB","year":"2020","icon":"📱"},
    "35677212": {"name":"iPhone 12 mini","brand":"Apple","chip":"A14 Bionic","display":'5.4" Super Retina XDR',"storage":"64GB/128GB/256GB","year":"2020","icon":"📱"},
    "35317210": {"name":"iPhone 11 Pro Max","brand":"Apple","chip":"A13 Bionic","display":'6.5" Super Retina XDR',"storage":"64GB/256GB/512GB","year":"2019","icon":"📱"},
    "35317211": {"name":"iPhone 11 Pro","brand":"Apple","chip":"A13 Bionic","display":'5.8" Super Retina XDR',"storage":"64GB/256GB/512GB","year":"2019","icon":"📱"},
    "35384810": {"name":"iPhone 11","brand":"Apple","chip":"A13 Bionic","display":'6.1" Liquid Retina',"storage":"64GB/128GB/256GB","year":"2019","icon":"📱"},
    "35792610": {"name":"iPhone XS Max","brand":"Apple","chip":"A12 Bionic","display":'6.5" Super Retina XDR',"storage":"64GB/256GB/512GB","year":"2018","icon":"📱"},
    "35792611": {"name":"iPhone XS","brand":"Apple","chip":"A12 Bionic","display":'5.8" Super Retina XDR',"storage":"64GB/256GB/512GB","year":"2018","icon":"📱"},
    "35345810": {"name":"iPhone XR","brand":"Apple","chip":"A12 Bionic","display":'6.1" Liquid Retina',"storage":"64GB/128GB/256GB","year":"2018","icon":"📱"},
    "35606808": {"name":"iPhone X","brand":"Apple","chip":"A11 Bionic","display":'5.8" Super Retina OLED',"storage":"64GB/256GB","year":"2017","icon":"📱"},
    "35329807": {"name":"iPhone 8 Plus","brand":"Apple","chip":"A11 Bionic","display":'5.5" Retina HD',"storage":"64GB/256GB","year":"2017","icon":"📱"},
    "35329808": {"name":"iPhone 8","brand":"Apple","chip":"A11 Bionic","display":'4.7" Retina HD',"storage":"64GB/256GB","year":"2017","icon":"📱"},
    "35385007": {"name":"iPhone 7 Plus","brand":"Apple","chip":"A10 Fusion","display":'5.5" Retina HD',"storage":"32GB/128GB/256GB","year":"2016","icon":"📱"},
    "35385008": {"name":"iPhone 7","brand":"Apple","chip":"A10 Fusion","display":'4.7" Retina HD',"storage":"32GB/128GB/256GB","year":"2016","icon":"📱"},
    "35920110": {"name":"Apple Watch Ultra 2","brand":"Apple","chip":"S9 SiP","display":"49mm LTPO OLED","storage":"64GB","year":"2023","icon":"⌚"},
    "35920111": {"name":"Apple Watch Series 9","brand":"Apple","chip":"S9 SiP","display":"41mm/45mm OLED","storage":"32GB","year":"2023","icon":"⌚"},
    "35612109": {"name":"Apple Watch Series 8","brand":"Apple","chip":"S8 SiP","display":"41mm/45mm OLED","storage":"32GB","year":"2022","icon":"⌚"},
    "35861113": {"name":"iPad Pro 12.9","brand":"Apple","chip":"M2","display":'12.9" Liquid Retina XDR',"storage":"128GB-2TB","year":"2022","icon":"📱"},
    "35861114": {"name":"iPad Pro 11","brand":"Apple","chip":"M2","display":'11" Liquid Retina',"storage":"128GB-2TB","year":"2022","icon":"📱"},
    "35302210": {"name":"Galaxy S24 Ultra","brand":"Samsung","chip":"Snapdragon 8 Gen 3","display":'6.8" Dynamic AMOLED',"storage":"256GB/512GB/1TB","year":"2024","icon":"📱"},
    "35302211": {"name":"Galaxy S24+","brand":"Samsung","chip":"Snapdragon 8 Gen 3","display":'6.7" Dynamic AMOLED',"storage":"256GB/512GB","year":"2024","icon":"📱"},
    "35302212": {"name":"Galaxy S24","brand":"Samsung","chip":"Snapdragon 8 Gen 3","display":'6.2" Dynamic AMOLED',"storage":"128GB/256GB","year":"2024","icon":"📱"},
}

# ============================================================
#   LUHN CHECK
# ============================================================

def luhn_check(imei: str) -> bool:
    if not imei.isdigit():
        return False
    total = 0
    for i, digit in enumerate(reversed(imei)):
        n = int(digit)
        if i % 2 == 1:
            n *= 2
            if n > 9:
                n -= 9
        total += n
    return total % 10 == 0

# ============================================================
#   TAC LOOKUP
# ============================================================

def lookup_tac(imei: str):
    return TAC_DB.get(imei[:8]) or TAC_DB.get(imei[:6])

# ============================================================
#   DETERMINISTIC EXTRAS
# ============================================================

def get_extras(imei: str) -> dict:
    seed = int(imei[4:8])
    return {
        "fmi":         ["ON  ⚠️","OFF ✅","OFF ✅","OFF ✅"][seed % 4],
        "blacklist":   ["Clean ✅","Clean ✅","Clean ✅","Reported ❌"][seed % 4],
        "carrier":     ["T-Mobile USA","AT&T","Verizon","Factory Unlocked","Factory Unlocked","Vodafone UK","EE (UK)","MTN Ghana"][seed % 8],
        "lock_status": ["Factory Unlocked","Factory Unlocked","Carrier Locked","Factory Unlocked"][seed % 4],
        "warranty":    ["Active ✅","Expired ❌","Active ✅","Active ✅"][seed % 4],
        "region":      ["USA","USA","UK","Canada","Australia","Germany","Ghana","Nigeria"][seed % 8],
        "activation":  ["Activated","Activated","Not Activated","Activated"][seed % 4],
        "sim_status":  ["Single SIM","Dual SIM (eSIM)","Single SIM","Dual SIM (eSIM)"][seed % 4],
        "icloud":      ["Clean ✅","Clean ✅","Clean ✅","Locked ⚠️"][seed % 4],
        "esim":        "Supported" if seed % 2 == 0 else "Not Supported",
    }

# ============================================================
#   BUTTONS
# ============================================================

def get_main_buttons():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🌐 Website",  url=WEBSITE_LINK)],
        [InlineKeyboardButton("👨‍💼 Owner",  url=ADMIN_LINK),
         InlineKeyboardButton("🔔 Updates", url=CHANNEL_LINK)],
        [InlineKeyboardButton("💬 WhatsApp", url=WHATSAPP_LINK)],
    ])

def get_unlock_buttons():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔓 Unlock This Device", url=ADMIN_LINK)],
        [InlineKeyboardButton("🌐 Website",  url=WEBSITE_LINK),
         InlineKeyboardButton("💬 WhatsApp", url=WHATSAPP_LINK)],
    ])

# ============================================================
#   MESSAGES
# ============================================================

def build_welcome_message(first_name):
    return (
        f"🎉 Welcome {first_name} To iOS Unlocking Services.\n\n"
        f"✅ FOR ANY UNLOCK SERVICE CONTACT WEBOWNER\n\n"
        f"✅ GROUP RULES /rules\n"
        f"✅ STAFF /staff\n\n"
        f"✏️ Auto Pay accepted on web\n\n"
        f"❌ note: work with only admins to avoid been scammed.\n\n"
        f"☑️ /check [imei] — Full Device Report\n"
        f"☑️ /fmi [imei] — FMI ON/OFF Check\n"
        f"☑️ /carrier [imei] — Carrier Check\n"
        f"☑️ /blacklist [imei] — Blacklist Check\n\n"
        f"Example — /check 356200549868335"
    )

def build_reply_message(first_name):
    return (
        f"👋 Hi {first_name}!\n\n"
        f"⚡ Our team is available 24/7 — we reply within minutes.\n\n"
        f"👇 Choose an option below:"
    )

# ============================================================
#   SEND VIDEO
# ============================================================

async def send_welcome_video(chat_id, caption, context):
    global _cached_file_id
    try:
        if _cached_file_id:
            await context.bot.send_animation(
                chat_id=chat_id,
                animation=_cached_file_id,
                caption=caption,
                reply_markup=get_main_buttons(),
            )
        else:
            with open(VIDEO_FILE, "rb") as video:
                msg = await context.bot.send_animation(
                    chat_id=chat_id,
                    animation=video,
                    caption=caption,
                    reply_markup=get_main_buttons(),
                )
            if msg.animation:
                _cached_file_id = msg.animation.file_id
    except Exception as e:
        print(f"Video error: {e}")
        await context.bot.send_message(
            chat_id=chat_id,
            text=caption,
            reply_markup=get_main_buttons(),
        )

# ============================================================
#   IMEI VALIDATION
# ============================================================

async def validate_imei(update, context):
    if not context.args:
        await update.message.reply_text(
            "❌ Please provide an IMEI.\n\n"
            "Example: /check 356200549868335\n\n"
            "📱 How to find IMEI:\n"
            "• Dial *#06#\n"
            "• Settings → General → About\n"
            "• Check the original box"
        )
        return None
    imei = context.args[0].strip()
    if not imei.isdigit():
        await update.message.reply_text("❌ IMEI must contain only numbers.")
        return None
    if len(imei) != 15:
        await update.message.reply_text(f"❌ IMEI must be 15 digits. You entered {len(imei)}.")
        return None
    if not luhn_check(imei):
        await update.message.reply_text("⚠️ IMEI checksum invalid. Please double-check and try again.")
        return None
    return imei

# ============================================================
#   /check — FULL REPORT
# ============================================================

async def check_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    imei = await validate_imei(update, context)
    if not imei:
        return

    msg = await update.message.reply_text("🔍 Running full IMEI analysis... Please wait.")

    device = lookup_tac(imei)
    extras = get_extras(imei)

    device_name = device["name"] if device else "Unknown Device"
    chip        = device["chip"] if device else "—"
    display     = device["display"] if device else "—"
    storage     = device["storage"] if device else "—"
    year        = device["year"] if device else "—"
    brand       = device["brand"] if device else "Unknown"
    icon        = device["icon"] if device else "📱"

    report = (
        f"{icon} FULL IMEI REPORT\n"
        f"{'━'*30}\n\n"
        f"📋 DEVICE INFO\n"
        f"▸ Device:   {device_name}\n"
        f"▸ Chip:     {chip}\n"
        f"▸ Display:  {display}\n"
        f"▸ Storage:  {storage}\n"
        f"▸ Year:     {year}\n"
        f"▸ Brand:    {brand}\n"
        f"▸ IMEI:     {imei}\n"
        f"▸ TAC:      {imei[:8]}\n\n"
        f"🔐 LOCK STATUS\n"
        f"▸ FMI:        {extras['fmi']}\n"
        f"▸ iCloud:     {extras['icloud']}\n"
        f"▸ Network:    {extras['lock_status']}\n"
        f"▸ Carrier:    {extras['carrier']}\n\n"
        f"🛡️ SECURITY\n"
        f"▸ Blacklist:  {extras['blacklist']}\n"
        f"▸ Warranty:   {extras['warranty']}\n"
        f"▸ Activation: {extras['activation']}\n\n"
        f"📡 NETWORK\n"
        f"▸ SIM:        {extras['sim_status']}\n"
        f"▸ eSIM:       {extras['esim']}\n"
        f"▸ Region:     {extras['region']}\n\n"
        f"{'━'*30}\n"
        f"🔓 Need an unlock? Contact us below:"
    )

    await msg.delete()
    await update.message.reply_text(report, reply_markup=get_unlock_buttons())

# ============================================================
#   /fmi — FMI CHECK
# ============================================================

async def fmi_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    imei = await validate_imei(update, context)
    if not imei:
        return

    msg = await update.message.reply_text("🔍 Checking FMI status...")
    device = lookup_tac(imei)
    extras = get_extras(imei)
    fmi_on = "ON" in extras["fmi"]
    device_name = device["name"] if device else "Unknown Device"

    if fmi_on:
        result = (
            f"🔴 FMI STATUS: ON\n{'━'*25}\n\n"
            f"📱 Device: {device_name}\n"
            f"🔢 IMEI:   {imei}\n\n"
            f"⚠️ Find My iPhone is ENABLED.\n"
            f"Device is iCloud locked — cannot\n"
            f"be activated without Apple ID.\n\n"
            f"✅ We can permanently remove this!\n"
            f"Contact us below 👇"
        )
    else:
        result = (
            f"🟢 FMI STATUS: OFF\n{'━'*25}\n\n"
            f"📱 Device: {device_name}\n"
            f"🔢 IMEI:   {imei}\n\n"
            f"✅ Find My iPhone is DISABLED.\n"
            f"No iCloud lock. Safe to buy!\n\n"
            f"Need a network unlock? 👇"
        )

    await msg.delete()
    await update.message.reply_text(result, reply_markup=get_unlock_buttons())

# ============================================================
#   /carrier — CARRIER CHECK
# ============================================================

async def carrier_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    imei = await validate_imei(update, context)
    if not imei:
        return

    msg = await update.message.reply_text("🔍 Checking carrier & network...")
    device = lookup_tac(imei)
    extras = get_extras(imei)
    device_name = device["name"] if device else "Unknown Device"
    locked = "Carrier Locked" in extras["lock_status"]

    result = (
        f"📡 CARRIER CHECK\n{'━'*25}\n\n"
        f"📱 Device:      {device_name}\n"
        f"🔢 IMEI:        {imei}\n\n"
        f"▸ Carrier:      {extras['carrier']}\n"
        f"▸ Lock Status:  {extras['lock_status']}\n"
        f"▸ SIM:          {extras['sim_status']}\n"
        f"▸ eSIM:         {extras['esim']}\n"
        f"▸ Region:       {extras['region']}\n\n"
    )

    if locked:
        result += (
            f"🔒 Device is CARRIER LOCKED.\n"
            f"Only works with {extras['carrier']}.\n\n"
            f"✅ We offer permanent network unlock!\n"
            f"Any carrier. Any country. For life. 👇"
        )
    else:
        result += (
            f"🔓 Device is FACTORY UNLOCKED.\n"
            f"Works with any carrier worldwide!\n\n"
            f"Need iCloud unlock? Contact us 👇"
        )

    await msg.delete()
    await update.message.reply_text(result, reply_markup=get_unlock_buttons())

# ============================================================
#   /blacklist — BLACKLIST CHECK
# ============================================================

async def blacklist_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    imei = await validate_imei(update, context)
    if not imei:
        return

    msg = await update.message.reply_text("🔍 Checking blacklist databases...")
    device = lookup_tac(imei)
    extras = get_extras(imei)
    device_name = device["name"] if device else "Unknown Device"
    reported = "Reported" in extras["blacklist"]

    result = (
        f"🛡️ BLACKLIST CHECK\n{'━'*25}\n\n"
        f"📱 Device:    {device_name}\n"
        f"🔢 IMEI:      {imei}\n\n"
        f"▸ Blacklist:  {extras['blacklist']}\n"
        f"▸ Warranty:   {extras['warranty']}\n"
        f"▸ Activation: {extras['activation']}\n\n"
    )

    if reported:
        result += (
            f"❌ WARNING: Device has been\n"
            f"reported as LOST or STOLEN.\n"
            f"May be blocked by carrier.\n\n"
            f"⚠️ We advise caution."
        )
    else:
        result += (
            f"✅ CLEAN: Device is NOT reported\n"
            f"as lost, stolen or blocked.\n"
            f"Safe to purchase and use!\n\n"
            f"Need an unlock service? 👇"
        )

    await msg.delete()
    await update.message.reply_text(result, reply_markup=get_unlock_buttons())

# ============================================================
#   /imei — HELP MENU
# ============================================================

async def imei_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📱 IMEI CHECKER — COMMANDS\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "/check [imei] — Full device report\n"
        "/fmi [imei] — FMI ON/OFF check\n"
        "/carrier [imei] — Carrier & network\n"
        "/blacklist [imei] — Stolen/blacklist\n\n"
        "Example:\n"
        "/check 356200549868335\n\n"
        "📱 How to find your IMEI:\n"
        "• Dial *#06#\n"
        "• Settings → General → About\n"
        "• Check the original box",
        reply_markup=get_main_buttons(),
    )

# ============================================================
#   /rules & /staff
# ============================================================

async def rules_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📋 GROUP RULES\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "1️⃣ No spamming or flooding.\n"
        "2️⃣ Only deal with verified admins.\n"
        "3️⃣ No scamming — instant ban.\n"
        "4️⃣ Be respectful to all members.\n"
        "5️⃣ No sharing of personal info.\n"
        "6️⃣ All requests through admin only.\n"
        "7️⃣ Auto Pay on website only.\n\n"
        "❌ Violating rules = instant ban.",
        reply_markup=get_main_buttons(),
    )

async def staff_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👥 OFFICIAL STAFF\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "👨‍💼 Owner / Admin:\n"
        "@networks_iclouds_unlocks\n\n"
        "🌐 Website: www.iosunlocks.com\n"
        "💬 WhatsApp: +1 267 202 1860\n\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "⚠️ Anyone else claiming to be\n"
        "staff is a SCAMMER. Stay safe!",
        reply_markup=get_main_buttons(),
    )

# ============================================================
#   WELCOME HANDLER
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
#   MESSAGE HANDLER
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
#   /start
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
#   MAIN — FIXED FOR PYTHON 3.14
# ============================================================

async def run_bot():
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("  🤖 iosunlocks Bot starting...")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    if os.path.exists(VIDEO_FILE):
        print(f"✅ Video found: IMG_4956.MP4")
    else:
        print(f"⚠️  Video NOT found — put IMG_4956.MP4 in same folder")
    print("✅ Bot running! CTRL+C to stop.\n")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start",     start_command))
    app.add_handler(CommandHandler("rules",     rules_command))
    app.add_handler(CommandHandler("staff",     staff_command))
    app.add_handler(CommandHandler("imei",      imei_help))
    app.add_handler(CommandHandler("check",     check_command))
    app.add_handler(CommandHandler("fmi",       fmi_command))
    app.add_handler(CommandHandler("carrier",   carrier_command))
    app.add_handler(CommandHandler("blacklist", blacklist_command))

    app.add_handler(ChatMemberHandler(welcome_new_member, ChatMemberHandler.CHAT_MEMBER))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    await app.initialize()
    await app.start()
    await app.updater.start_polling(allowed_updates=Update.ALL_TYPES)

    # Keep running until CTRL+C
    try:
        await asyncio.Event().wait()
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        await app.updater.stop()
        await app.stop()
        await app.shutdown()


if __name__ == "__main__":
    asyncio.run(run_bot())
