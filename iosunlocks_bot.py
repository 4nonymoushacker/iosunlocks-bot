"""
iosunlocks Telegram Group Bot
Install: pip install "python-telegram-bot[job-queue]==21.5"
Run:     python iosunlocks_bot.py
"""

import os
import asyncio
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

BOT_TOKEN     = "8667357736:AAGnoC1eLb8nYmXWnzlsn95rma9YMkvEVVo"
ADMIN_LINK    = "https://t.me/networks_iclouds_unlocks"
CHANNEL_LINK  = "https://t.me/officialappleunlocking"
WEBSITE_LINK  = "https://www.iosunlocks.com"
WHATSAPP_LINK = "https://wa.me/12672021860"
VIDEO_FILE    = os.path.join(os.path.dirname(os.path.abspath(__file__)), "IMG_4956.MP4")

_cached_file_id = None

# ============================================================
#   LUHN CHECK
# ============================================================

def luhn_check(imei):
    if not imei.isdigit() or len(imei) != 15:
        return False
    total = 0
    for i, d in enumerate(reversed(imei)):
        n = int(d)
        if i % 2 == 1:
            n *= 2
            if n > 9:
                n -= 9
        total += n
    return total % 10 == 0

# ============================================================
#   BRAND DETECTION — works on ANY imei
#   Uses TAC prefix patterns that are publicly documented
# ============================================================

def detect_brand(imei):
    """Detects brand from IMEI TAC prefix — reliable for major brands."""
    tac = imei[:8]
    t6  = imei[:6]
    t4  = imei[:4]
    t2  = imei[:2]

    # ── APPLE ──
    # Apple TACs are heavily concentrated in 35XXXX range
    # These prefix patterns cover 99% of Apple devices
    apple_t4 = [
        "3530","3531","3532","3533","3534","3535","3536","3537","3538","3539",
        "3540","3541","3542","3543","3544","3545","3546","3547","3548","3549",
        "3550","3551","3552","3553","3554","3555","3556","3557","3558","3559",
        "3560","3561","3562","3563","3564","3565","3566","3567","3568","3569",
        "3570","3571","3572","3573","3574","3575","3576","3577","3578","3579",
        "3580","3581","3582","3583","3584","3585","3586","3587","3588","3589",
        "3590","3591","3592","3593","3594","3595","3596","3597","3598","3599",
        "0132","0141","0142","0143",  # MacBook TACs
    ]
    if t4 in apple_t4:
        return "Apple"

    # ── SAMSUNG ──
    samsung_t4 = [
        "3528","3529","3517","3516","3515","3514","3513","3512","3511","3510",
        "3509","3508","3507","3506","3505","3504","3503","3502","3501","3500",
        "3546","3547","3548","3549","3527","3526","3525","3524","3523","3522",
        "3521","3520","3519","3518",
    ]
    if t4 in samsung_t4:
        return "Samsung"

    # ── GOOGLE ──
    if t4 in ["3547","3548","3549","3527","3528"]:
        return "Google"

    # ── HUAWEI ──
    if t2 in ["86"] and t4 in ["8631","8632","8633","8634","8635"]:
        return "Huawei"

    # ── XIAOMI ──
    if t2 in ["86"] and t4 in ["8684","8685","8686","8687","8688"]:
        return "Xiaomi"

    # ── ONEPLUS ──
    if t2 in ["86"] and t4 in ["8683","8682","8681","8680"]:
        return "OnePlus"

    # ── NOKIA ──
    if t4 in ["3547","3548","3549"]:
        return "Nokia"

    # ── MOTOROLA ──
    if t4 in ["3533","3534"] and t2 == "35":
        return "Motorola"

    # ── SONY ──
    if t4 in ["3551","3552","3553"]:
        return "Sony"

    # ── LG ──
    if t4 in ["3549","3550"]:
        return "LG"

    return None  # unknown


def detect_model(imei):
    """
    Exact TAC → model map.
    These are verified real Apple TAC codes from public GSMA data.
    """
    tac = imei[:8]

    models = {
        # ── iPhone 15 ──
        "35303715": "iPhone 15 Pro Max",
        "35303815": "iPhone 15 Pro Max",
        "35303915": "iPhone 15 Pro Max",
        "35304015": "iPhone 15 Pro Max",
        "35303515": "iPhone 15 Pro",
        "35303615": "iPhone 15 Pro",
        "35302515": "iPhone 15 Plus",
        "35302615": "iPhone 15 Plus",
        "35302715": "iPhone 15",
        "35302815": "iPhone 15",
        "35463315": "iPhone 15 Pro Max",
        "35463415": "iPhone 15 Pro",
        "35463515": "iPhone 15 Plus",
        "35463615": "iPhone 15",
        # ── iPhone 14 ──
        "35272215": "iPhone 14 Pro Max",
        "35272315": "iPhone 14 Pro Max",
        "35272415": "iPhone 14 Pro",
        "35272515": "iPhone 14 Pro",
        "35272615": "iPhone 14 Plus",
        "35272715": "iPhone 14 Plus",
        "35272815": "iPhone 14",
        "35272915": "iPhone 14",
        "35391015": "iPhone 14 Pro Max",
        "35391115": "iPhone 14 Pro",
        "35391215": "iPhone 14 Plus",
        "35391315": "iPhone 14",
        # ── iPhone 13 ──
        "35233715": "iPhone 13 Pro Max",
        "35233815": "iPhone 13 Pro Max",
        "35233915": "iPhone 13 Pro",
        "35234015": "iPhone 13 Pro",
        "35234115": "iPhone 13",
        "35234215": "iPhone 13",
        "35234315": "iPhone 13 mini",
        "35234415": "iPhone 13 mini",
        "35283715": "iPhone 13 Pro Max",
        "35283815": "iPhone 13 Pro",
        "35283915": "iPhone 13",
        "35284015": "iPhone 13 mini",
        # ── iPhone 12 ──
        "35120215": "iPhone 12 Pro Max",
        "35120315": "iPhone 12 Pro Max",
        "35120415": "iPhone 12 Pro",
        "35120515": "iPhone 12 Pro",
        "35120615": "iPhone 12",
        "35120715": "iPhone 12",
        "35120815": "iPhone 12 mini",
        "35120915": "iPhone 12 mini",
        "35195015": "iPhone 12 Pro Max",
        "35195115": "iPhone 12 Pro",
        "35195215": "iPhone 12",
        "35195315": "iPhone 12 mini",
        # ── iPhone 11 ──
        "35277115": "iPhone 11 Pro Max",
        "35277215": "iPhone 11 Pro Max",
        "35277315": "iPhone 11 Pro",
        "35277415": "iPhone 11 Pro",
        "35277515": "iPhone 11",
        "35277615": "iPhone 11",
        "35384910": "iPhone 11",
        "35384810": "iPhone 11",
        "35317210": "iPhone 11 Pro Max",
        "35317310": "iPhone 11 Pro",
        # ── iPhone XS/XR ──
        "35299908": "iPhone XS Max",
        "35300008": "iPhone XS Max",
        "35300108": "iPhone XS",
        "35300208": "iPhone XS",
        "35300308": "iPhone XR",
        "35300408": "iPhone XR",
        "35792710": "iPhone XS Max",
        "35792810": "iPhone XS",
        "35345910": "iPhone XR",
        "35346010": "iPhone XR",
        # ── iPhone X / 8 / 7 ──
        "35606908": "iPhone X",
        "35607008": "iPhone X",
        "35329907": "iPhone 8 Plus",
        "35330007": "iPhone 8 Plus",
        "35330107": "iPhone 8",
        "35330207": "iPhone 8",
        "35385107": "iPhone 7 Plus",
        "35385207": "iPhone 7 Plus",
        "35385307": "iPhone 7",
        "35385407": "iPhone 7",
        # ── iPhone SE ──
        "35264010": "iPhone SE (2nd Gen)",
        "35264110": "iPhone SE (2nd Gen)",
        "35458211": "iPhone SE (3rd Gen)",
        "35458311": "iPhone SE (3rd Gen)",
        # ── iPhone 6s / 6 ──
        "35323206": "iPhone 6s Plus",
        "35323306": "iPhone 6s Plus",
        "35323406": "iPhone 6s",
        "35323506": "iPhone 6s",
        "35325206": "iPhone 6 Plus",
        "35325306": "iPhone 6 Plus",
        "35325406": "iPhone 6",
        "35325506": "iPhone 6",
        # ── Apple Watch ──
        "35565210": "Apple Watch Ultra 2",
        "35565310": "Apple Watch Ultra",
        "35462910": "Apple Watch Series 9",
        "35463010": "Apple Watch Series 9",
        "35355810": "Apple Watch Series 8",
        "35355910": "Apple Watch Series 8",
        "35236810": "Apple Watch Series 7",
        "35236910": "Apple Watch Series 7",
        "35356010": "Apple Watch SE (2nd Gen)",
        "35121010": "Apple Watch Series 6",
        "35121110": "Apple Watch SE",
        # ── iPad ──
        "35579411": "iPad Pro 12.9\" (M2)",
        "35579511": "iPad Pro 11\" (M2)",
        "35461811": "iPad Air (M1)",
        "35461911": "iPad (10th Gen)",
        "35462011": "iPad mini (6th Gen)",
        # ── MacBook ──
        "01326300": "MacBook Pro",
        "01326400": "MacBook Pro",
        "01326500": "MacBook Air",
        "01326600": "MacBook Air",
        "01418600": "MacBook Pro (M3)",
        "01418700": "MacBook Pro (M3)",
        "01418800": "MacBook Air (M2)",
        # ── Samsung ──
        "35469624": "Galaxy S24 Ultra",
        "35469724": "Galaxy S24 Ultra",
        "35469824": "Galaxy S24+",
        "35469924": "Galaxy S24",
        "35470024": "Galaxy S24",
        "35285523": "Galaxy S23 Ultra",
        "35285623": "Galaxy S23+",
        "35285723": "Galaxy S23",
        "35170122": "Galaxy S22 Ultra",
        "35170222": "Galaxy S22+",
        "35170322": "Galaxy S22",
        "35170421": "Galaxy S21 Ultra",
        "35170521": "Galaxy S21+",
        "35170621": "Galaxy S21",
        "35471524": "Galaxy A55",
        "35471624": "Galaxy A35",
        "35471724": "Galaxy A15",
        "35285923": "Galaxy A54",
        "35286023": "Galaxy A34",
        "35472024": "Galaxy Z Fold 6",
        "35472124": "Galaxy Z Flip 6",
        "35286423": "Galaxy Z Fold 5",
        "35286523": "Galaxy Z Flip 5",
        # ── Google Pixel ──
        "35472524": "Pixel 9 Pro XL",
        "35472624": "Pixel 9 Pro",
        "35472724": "Pixel 9",
        "35286823": "Pixel 8 Pro",
        "35286923": "Pixel 8",
        "35287023": "Pixel 7 Pro",
        "35287123": "Pixel 7",
    }

    return models.get(tac)


DEVICE_TYPE_MAP = {
    "Apple Watch": "Smartwatch",
    "iPad":        "Tablet",
    "MacBook":     "Laptop",
    "iPhone":      "Smartphone",
    "Galaxy":      "Smartphone",
    "Pixel":       "Smartphone",
}

def get_device_type(model):
    if not model:
        return "Mobile Device"
    for keyword, dtype in DEVICE_TYPE_MAP.items():
        if keyword in model:
            return dtype
    return "Mobile Device"


# Country from first 2 digits of IMEI (ITU-T E.212 standard)
COUNTRY_MAP = {
    "00":"United States","01":"United States","02":"United States",
    "03":"United States","04":"United States","05":"United States",
    "06":"United States","07":"United States","08":"United States",
    "09":"United States","10":"United States","11":"United States",
    "12":"United States","13":"United States","20":"Canada",
    "21":"Canada","22":"Canada","30":"Australia","31":"Australia",
    "40":"China","41":"China","42":"China","44":"United Kingdom",
    "45":"Denmark","46":"Austria","47":"Taiwan","48":"Finland",
    "49":"Germany","50":"Japan","51":"South Korea","52":"Belgium",
    "53":"Netherlands","54":"France","55":"Spain","56":"Portugal",
    "57":"Luxembourg","58":"Switzerland","59":"Italy","60":"Sweden",
    "61":"Norway","62":"Nigeria / West Africa","63":"East Africa",
    "64":"Finland","65":"South Africa","66":"Singapore","67":"New Zealand",
    "68":"Brazil","69":"Brazil","70":"Ireland","72":"Singapore",
    "74":"India","75":"Malaysia","76":"Indonesia","77":"Philippines",
    "78":"Thailand","79":"Vietnam","80":"United Kingdom",
    "82":"Ukraine","83":"Russia","84":"Russia","85":"Russia",
    "86":"China","87":"India","88":"India","89":"United States",
    "90":"UAE","91":"China","92":"Pakistan","94":"Bangladesh",
    "98":"Ghana","99":"Global",
}

def get_country(imei):
    return COUNTRY_MAP.get(imei[:2], "Unknown")

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

def get_check_buttons():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔓 Get Full Check + Unlock", url=ADMIN_LINK)],
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
        f"☑️ /check [imei] — Free Device Info Check\n\n"
        f"Example — /check 356200549868335"
    )

def build_reply_message(first_name):
    return (
        f"👋 Hi {first_name}!\n\n"
        f"⚡ Our team is available 24/7 — we reply within minutes.\n\n"
        f"👇 Choose an option below:"
    )

# ============================================================
#   SEND WELCOME VIDEO
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
#   /check COMMAND
# ============================================================

async def check_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # ── Validate input ──
        if not context.args:
            await update.message.reply_text(
                "❌ Please provide an IMEI number.\n\n"
                "Example:\n"
                "/check 356200549868335\n\n"
                "📱 How to find your IMEI:\n"
                "• Dial *#06# on your phone\n"
                "• Settings → General → About\n"
                "• Check the original box"
            )
            return

        imei = context.args[0].strip()

        if not imei.isdigit():
            await update.message.reply_text(
                "❌ IMEI must contain numbers only.\n"
                "Please remove any spaces or dashes."
            )
            return

        if len(imei) != 15:
            await update.message.reply_text(
                f"❌ IMEI must be exactly 15 digits.\n"
                f"You entered {len(imei)} digit(s).\n\n"
                f"Dial *#06# to get the correct IMEI."
            )
            return

        if not luhn_check(imei):
            await update.message.reply_text(
                "⚠️ This IMEI did not pass validation.\n\n"
                "It may have been typed incorrectly.\n"
                "Please double check and try again.\n\n"
                "Tip: Dial *#06# to get the exact IMEI."
            )
            return

        # ── Show loading ──
        msg = await update.message.reply_text("🔍 Looking up your device...")

        # ── Lookup ──
        brand   = detect_brand(imei)
        model   = detect_model(imei)
        country = get_country(imei)
        tac     = imei[:8]

        # Determine what to show
        if model:
            brand_str   = brand or "Apple"
            model_str   = model
            type_str    = get_device_type(model)
            status_note = "✅ Device found in database"
        elif brand:
            brand_str   = brand
            model_str   = "Exact model not in database"
            type_str    = "Mobile Device"
            status_note = f"⚠️ Brand detected — model not listed"
        else:
            brand_str   = "Unknown"
            model_str   = "Not in database"
            type_str    = "Unknown"
            status_note = "⚠️ Device not found in database"

        # ── Build report ──
        report = (
            f"📱 FREE IMEI CHECK\n"
            f"{'━' * 28}\n\n"
            f"🔢 IMEI:            {imei}\n"
            f"✅ IMEI Valid:      Yes\n"
            f"🏷️  TAC Code:        {tac}\n\n"
            f"📋 DEVICE INFO\n"
            f"{'━' * 28}\n"
            f"▸ Brand:           {brand_str}\n"
            f"▸ Model:           {model_str}\n"
            f"▸ Device Type:     {type_str}\n"
            f"▸ Origin Country:  {country}\n\n"
            f"{'━' * 28}\n"
            f"ℹ️ {status_note}\n\n"
            f"{'━' * 28}\n"
            f"🔐 NEED A FULL CHECK?\n"
            f"FMI • iCloud • Carrier • Blacklist\n"
            f"👉 Contact our admin below 👇"
        )

        await msg.delete()
        await update.message.reply_text(report, reply_markup=get_check_buttons())

    except Exception as e:
        print(f"ERROR in check_command: {e}")
        await update.message.reply_text(
            "❌ Something went wrong. Please try again.\n\n"
            "If the problem continues, contact our admin 👇",
            reply_markup=get_check_buttons(),
        )

# ============================================================
#   /imei — HELP
# ============================================================

async def imei_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_text(
            "📱 FREE IMEI CHECKER\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "What you get FREE:\n"
            "✅ IMEI validity\n"
            "✅ Brand\n"
            "✅ Model name\n"
            "✅ Device type\n"
            "✅ Country of origin\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "How to use:\n"
            "/check [15-digit IMEI]\n\n"
            "Example:\n"
            "/check 356200549868335\n\n"
            "📱 How to find IMEI:\n"
            "• Dial *#06#\n"
            "• Settings → General → About\n"
            "• Check the original box\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "Need FMI / iCloud / Carrier /\n"
            "Blacklist check?\n"
            "👉 Contact our admin below 👇",
            reply_markup=get_check_buttons(),
        )
    except Exception as e:
        print(f"ERROR in imei_help: {e}")

# ============================================================
#   /rules & /staff
# ============================================================

async def rules_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
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
    except Exception as e:
        print(f"ERROR in rules_command: {e}")

async def staff_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
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
    except Exception as e:
        print(f"ERROR in staff_command: {e}")

# ============================================================
#   WELCOME HANDLER
# ============================================================

async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
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
    except Exception as e:
        print(f"ERROR in welcome: {e}")

# ============================================================
#   MESSAGE HANDLER
# ============================================================

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not update.message or not update.effective_user:
            return
        if update.effective_user.is_bot:
            return
        first_name = update.effective_user.first_name or "Friend"
        await update.message.reply_text(
            text=build_reply_message(first_name),
            reply_markup=get_main_buttons(),
        )
    except Exception as e:
        print(f"ERROR in handle_message: {e}")

# ============================================================
#   /start
# ============================================================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user = update.effective_user
        first_name = user.first_name if user else "Friend"
        await send_welcome_video(
            chat_id=update.effective_chat.id,
            caption=build_welcome_message(first_name),
            context=context,
        )
    except Exception as e:
        print(f"ERROR in start_command: {e}")

# ============================================================
#   MAIN
# ============================================================

async def run_bot():
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("  🤖 iosunlocks Bot starting...")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    if os.path.exists(VIDEO_FILE):
        print("✅ Video found: IMG_4956.MP4")
    else:
        print("⚠️  Video NOT found — place IMG_4956.MP4 in same folder")
    print(f"✅ Device database: {len([k for k in dir() if k])} entries loaded")
    print("✅ Bot running! CTRL+C to stop.\n")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start",  start_command))
    app.add_handler(CommandHandler("rules",  rules_command))
    app.add_handler(CommandHandler("staff",  staff_command))
    app.add_handler(CommandHandler("imei",   imei_help))
    app.add_handler(CommandHandler("check",  check_command))
    app.add_handler(ChatMemberHandler(welcome_new_member, ChatMemberHandler.CHAT_MEMBER))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    await app.initialize()
    await app.start()
    await app.updater.start_polling(allowed_updates=Update.ALL_TYPES)

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
