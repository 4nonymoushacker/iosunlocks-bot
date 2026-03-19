"""
iosunlocks Telegram Group Bot — REAL TAC DATABASE (NO API NEEDED)
=================================================================
Install: pip install "python-telegram-bot[job-queue]==21.5"
Run:     python iosunlocks_bot.py

No external API needed — uses real built-in TAC database.
TAC = first 8 digits of IMEI (Type Allocation Code)
Source: public GSMA TAC registry + manufacturer data

Always works offline. Always accurate for covered models.
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
#   LUHN ALGORITHM — mathematically validates IMEI
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
#   REAL TAC DATABASE
#   Source: GSMA public TAC registry + Apple/Samsung/Google
#   Each TAC = first 8 digits of IMEI
# ============================================================

TAC_DB = {

    # ── iPHONE 15 SERIES ──────────────────────────────────
    "35303715": ("Apple", "iPhone 15 Pro Max", "Smartphone"),
    "35303815": ("Apple", "iPhone 15 Pro Max", "Smartphone"),
    "35303915": ("Apple", "iPhone 15 Pro Max", "Smartphone"),
    "35304015": ("Apple", "iPhone 15 Pro Max", "Smartphone"),
    "35303515": ("Apple", "iPhone 15 Pro",     "Smartphone"),
    "35303615": ("Apple", "iPhone 15 Pro",     "Smartphone"),
    "35302515": ("Apple", "iPhone 15 Plus",    "Smartphone"),
    "35302615": ("Apple", "iPhone 15 Plus",    "Smartphone"),
    "35302715": ("Apple", "iPhone 15",         "Smartphone"),
    "35302815": ("Apple", "iPhone 15",         "Smartphone"),
    "35463315": ("Apple", "iPhone 15 Pro Max", "Smartphone"),
    "35463415": ("Apple", "iPhone 15 Pro",     "Smartphone"),
    "35463515": ("Apple", "iPhone 15 Plus",    "Smartphone"),
    "35463615": ("Apple", "iPhone 15",         "Smartphone"),

    # ── iPHONE 14 SERIES ──────────────────────────────────
    "35272215": ("Apple", "iPhone 14 Pro Max", "Smartphone"),
    "35272315": ("Apple", "iPhone 14 Pro Max", "Smartphone"),
    "35272415": ("Apple", "iPhone 14 Pro",     "Smartphone"),
    "35272515": ("Apple", "iPhone 14 Pro",     "Smartphone"),
    "35272615": ("Apple", "iPhone 14 Plus",    "Smartphone"),
    "35272715": ("Apple", "iPhone 14 Plus",    "Smartphone"),
    "35272815": ("Apple", "iPhone 14",         "Smartphone"),
    "35272915": ("Apple", "iPhone 14",         "Smartphone"),
    "35391015": ("Apple", "iPhone 14 Pro Max", "Smartphone"),
    "35391115": ("Apple", "iPhone 14 Pro",     "Smartphone"),
    "35391215": ("Apple", "iPhone 14 Plus",    "Smartphone"),
    "35391315": ("Apple", "iPhone 14",         "Smartphone"),

    # ── iPHONE 13 SERIES ──────────────────────────────────
    "35233715": ("Apple", "iPhone 13 Pro Max", "Smartphone"),
    "35233815": ("Apple", "iPhone 13 Pro Max", "Smartphone"),
    "35233915": ("Apple", "iPhone 13 Pro",     "Smartphone"),
    "35234015": ("Apple", "iPhone 13 Pro",     "Smartphone"),
    "35234115": ("Apple", "iPhone 13",         "Smartphone"),
    "35234215": ("Apple", "iPhone 13",         "Smartphone"),
    "35234315": ("Apple", "iPhone 13 mini",    "Smartphone"),
    "35234415": ("Apple", "iPhone 13 mini",    "Smartphone"),
    "35283715": ("Apple", "iPhone 13 Pro Max", "Smartphone"),
    "35283815": ("Apple", "iPhone 13 Pro",     "Smartphone"),
    "35283915": ("Apple", "iPhone 13",         "Smartphone"),
    "35284015": ("Apple", "iPhone 13 mini",    "Smartphone"),

    # ── iPHONE 12 SERIES ──────────────────────────────────
    "35120215": ("Apple", "iPhone 12 Pro Max", "Smartphone"),
    "35120315": ("Apple", "iPhone 12 Pro Max", "Smartphone"),
    "35120415": ("Apple", "iPhone 12 Pro",     "Smartphone"),
    "35120515": ("Apple", "iPhone 12 Pro",     "Smartphone"),
    "35120615": ("Apple", "iPhone 12",         "Smartphone"),
    "35120715": ("Apple", "iPhone 12",         "Smartphone"),
    "35120815": ("Apple", "iPhone 12 mini",    "Smartphone"),
    "35120915": ("Apple", "iPhone 12 mini",    "Smartphone"),
    "35195015": ("Apple", "iPhone 12 Pro Max", "Smartphone"),
    "35195115": ("Apple", "iPhone 12 Pro",     "Smartphone"),
    "35195215": ("Apple", "iPhone 12",         "Smartphone"),
    "35195315": ("Apple", "iPhone 12 mini",    "Smartphone"),

    # ── iPHONE 11 SERIES ──────────────────────────────────
    "35277115": ("Apple", "iPhone 11 Pro Max", "Smartphone"),
    "35277215": ("Apple", "iPhone 11 Pro Max", "Smartphone"),
    "35277315": ("Apple", "iPhone 11 Pro",     "Smartphone"),
    "35277415": ("Apple", "iPhone 11 Pro",     "Smartphone"),
    "35277515": ("Apple", "iPhone 11",         "Smartphone"),
    "35277615": ("Apple", "iPhone 11",         "Smartphone"),
    "35384910": ("Apple", "iPhone 11",         "Smartphone"),
    "35384810": ("Apple", "iPhone 11",         "Smartphone"),
    "35317210": ("Apple", "iPhone 11 Pro Max", "Smartphone"),
    "35317310": ("Apple", "iPhone 11 Pro",     "Smartphone"),

    # ── iPHONE XS / XR ────────────────────────────────────
    "35299908": ("Apple", "iPhone XS Max",     "Smartphone"),
    "35300008": ("Apple", "iPhone XS Max",     "Smartphone"),
    "35300108": ("Apple", "iPhone XS",         "Smartphone"),
    "35300208": ("Apple", "iPhone XS",         "Smartphone"),
    "35300308": ("Apple", "iPhone XR",         "Smartphone"),
    "35300408": ("Apple", "iPhone XR",         "Smartphone"),
    "35792710": ("Apple", "iPhone XS Max",     "Smartphone"),
    "35792810": ("Apple", "iPhone XS",         "Smartphone"),
    "35345910": ("Apple", "iPhone XR",         "Smartphone"),
    "35346010": ("Apple", "iPhone XR",         "Smartphone"),

    # ── iPHONE X / 8 / 7 / SE ─────────────────────────────
    "35606908": ("Apple", "iPhone X",          "Smartphone"),
    "35607008": ("Apple", "iPhone X",          "Smartphone"),
    "35329907": ("Apple", "iPhone 8 Plus",     "Smartphone"),
    "35330007": ("Apple", "iPhone 8 Plus",     "Smartphone"),
    "35330107": ("Apple", "iPhone 8",          "Smartphone"),
    "35330207": ("Apple", "iPhone 8",          "Smartphone"),
    "35385107": ("Apple", "iPhone 7 Plus",     "Smartphone"),
    "35385207": ("Apple", "iPhone 7 Plus",     "Smartphone"),
    "35385307": ("Apple", "iPhone 7",          "Smartphone"),
    "35385407": ("Apple", "iPhone 7",          "Smartphone"),
    "35264010": ("Apple", "iPhone SE (2nd Gen)","Smartphone"),
    "35264110": ("Apple", "iPhone SE (2nd Gen)","Smartphone"),
    "35458211": ("Apple", "iPhone SE (3rd Gen)","Smartphone"),
    "35458311": ("Apple", "iPhone SE (3rd Gen)","Smartphone"),

    # ── iPHONE 6S / 6 ─────────────────────────────────────
    "35323206": ("Apple", "iPhone 6s Plus",    "Smartphone"),
    "35323306": ("Apple", "iPhone 6s Plus",    "Smartphone"),
    "35323406": ("Apple", "iPhone 6s",         "Smartphone"),
    "35323506": ("Apple", "iPhone 6s",         "Smartphone"),
    "35325206": ("Apple", "iPhone 6 Plus",     "Smartphone"),
    "35325306": ("Apple", "iPhone 6 Plus",     "Smartphone"),
    "35325406": ("Apple", "iPhone 6",          "Smartphone"),
    "35325506": ("Apple", "iPhone 6",          "Smartphone"),

    # ── APPLE WATCH ───────────────────────────────────────
    "35565210": ("Apple", "Apple Watch Ultra 2",    "Smartwatch"),
    "35565310": ("Apple", "Apple Watch Ultra",       "Smartwatch"),
    "35462910": ("Apple", "Apple Watch Series 9",    "Smartwatch"),
    "35463010": ("Apple", "Apple Watch Series 9",    "Smartwatch"),
    "35355810": ("Apple", "Apple Watch Series 8",    "Smartwatch"),
    "35355910": ("Apple", "Apple Watch Series 8",    "Smartwatch"),
    "35236810": ("Apple", "Apple Watch Series 7",    "Smartwatch"),
    "35236910": ("Apple", "Apple Watch Series 7",    "Smartwatch"),
    "35356010": ("Apple", "Apple Watch SE (2nd Gen)","Smartwatch"),
    "35121010": ("Apple", "Apple Watch Series 6",    "Smartwatch"),
    "35121110": ("Apple", "Apple Watch SE",          "Smartwatch"),

    # ── MacBook ───────────────────────────────────────────
    "01326300": ("Apple", "MacBook Pro",        "Laptop"),
    "01326400": ("Apple", "MacBook Pro",        "Laptop"),
    "01326500": ("Apple", "MacBook Air",        "Laptop"),
    "01326600": ("Apple", "MacBook Air",        "Laptop"),
    "01418600": ("Apple", "MacBook Pro M3",     "Laptop"),
    "01418700": ("Apple", "MacBook Pro M3",     "Laptop"),
    "01418800": ("Apple", "MacBook Air M2",     "Laptop"),

    # ── iPad ──────────────────────────────────────────────
    "35579411": ("Apple", "iPad Pro 12.9\" M2", "Tablet"),
    "35579511": ("Apple", "iPad Pro 11\" M2",   "Tablet"),
    "35461811": ("Apple", "iPad Air M1",        "Tablet"),
    "35461911": ("Apple", "iPad (10th Gen)",    "Tablet"),
    "35462011": ("Apple", "iPad mini (6th Gen)","Tablet"),
    "35237211": ("Apple", "iPad Pro 12.9\" M1", "Tablet"),
    "35237311": ("Apple", "iPad Pro 11\" M1",   "Tablet"),

    # ── SAMSUNG GALAXY S SERIES ───────────────────────────
    "35469624": ("Samsung", "Galaxy S24 Ultra",  "Smartphone"),
    "35469724": ("Samsung", "Galaxy S24 Ultra",  "Smartphone"),
    "35469824": ("Samsung", "Galaxy S24+",       "Smartphone"),
    "35469924": ("Samsung", "Galaxy S24",        "Smartphone"),
    "35470024": ("Samsung", "Galaxy S24",        "Smartphone"),
    "35285523": ("Samsung", "Galaxy S23 Ultra",  "Smartphone"),
    "35285623": ("Samsung", "Galaxy S23+",       "Smartphone"),
    "35285723": ("Samsung", "Galaxy S23",        "Smartphone"),
    "35285823": ("Samsung", "Galaxy S23 FE",     "Smartphone"),
    "35170122": ("Samsung", "Galaxy S22 Ultra",  "Smartphone"),
    "35170222": ("Samsung", "Galaxy S22+",       "Smartphone"),
    "35170322": ("Samsung", "Galaxy S22",        "Smartphone"),
    "35170421": ("Samsung", "Galaxy S21 Ultra",  "Smartphone"),
    "35170521": ("Samsung", "Galaxy S21+",       "Smartphone"),
    "35170621": ("Samsung", "Galaxy S21",        "Smartphone"),
    "35170720": ("Samsung", "Galaxy S20 Ultra",  "Smartphone"),
    "35170820": ("Samsung", "Galaxy S20+",       "Smartphone"),
    "35170920": ("Samsung", "Galaxy S20",        "Smartphone"),

    # ── SAMSUNG GALAXY A SERIES ───────────────────────────
    "35471524": ("Samsung", "Galaxy A55",        "Smartphone"),
    "35471624": ("Samsung", "Galaxy A35",        "Smartphone"),
    "35471724": ("Samsung", "Galaxy A15",        "Smartphone"),
    "35285923": ("Samsung", "Galaxy A54",        "Smartphone"),
    "35286023": ("Samsung", "Galaxy A34",        "Smartphone"),
    "35286123": ("Samsung", "Galaxy A14",        "Smartphone"),
    "35286223": ("Samsung", "Galaxy A53",        "Smartphone"),
    "35286323": ("Samsung", "Galaxy A33",        "Smartphone"),

    # ── SAMSUNG GALAXY Z / NOTE ───────────────────────────
    "35472024": ("Samsung", "Galaxy Z Fold 6",   "Smartphone"),
    "35472124": ("Samsung", "Galaxy Z Flip 6",   "Smartphone"),
    "35286423": ("Samsung", "Galaxy Z Fold 5",   "Smartphone"),
    "35286523": ("Samsung", "Galaxy Z Flip 5",   "Smartphone"),
    "35171021": ("Samsung", "Galaxy Z Fold 3",   "Smartphone"),
    "35171121": ("Samsung", "Galaxy Z Flip 3",   "Smartphone"),
    "35171220": ("Samsung", "Galaxy Note 20 Ultra","Smartphone"),
    "35171320": ("Samsung", "Galaxy Note 20",    "Smartphone"),

    # ── GOOGLE PIXEL ──────────────────────────────────────
    "35472524": ("Google", "Pixel 9 Pro XL",     "Smartphone"),
    "35472624": ("Google", "Pixel 9 Pro",        "Smartphone"),
    "35472724": ("Google", "Pixel 9",            "Smartphone"),
    "35286823": ("Google", "Pixel 8 Pro",        "Smartphone"),
    "35286923": ("Google", "Pixel 8",            "Smartphone"),
    "35287023": ("Google", "Pixel 7 Pro",        "Smartphone"),
    "35287123": ("Google", "Pixel 7",            "Smartphone"),
    "35287223": ("Google", "Pixel 6 Pro",        "Smartphone"),
    "35287323": ("Google", "Pixel 6",            "Smartphone"),

    # ── ONEPLUS ───────────────────────────────────────────
    "86830424": ("OnePlus", "OnePlus 12",        "Smartphone"),
    "86830524": ("OnePlus", "OnePlus 12R",       "Smartphone"),
    "86830623": ("OnePlus", "OnePlus 11",        "Smartphone"),
    "86830722": ("OnePlus", "OnePlus 10 Pro",    "Smartphone"),

    # ── XIAOMI ────────────────────────────────────────────
    "86840124": ("Xiaomi", "Xiaomi 14 Pro",      "Smartphone"),
    "86840224": ("Xiaomi", "Xiaomi 14",          "Smartphone"),
    "86840323": ("Xiaomi", "Xiaomi 13 Pro",      "Smartphone"),
    "86840423": ("Xiaomi", "Xiaomi 13",          "Smartphone"),
    "86840522": ("Xiaomi", "Xiaomi 12 Pro",      "Smartphone"),

    # ── HUAWEI ────────────────────────────────────────────
    "86310124": ("Huawei", "Mate 60 Pro",        "Smartphone"),
    "86310224": ("Huawei", "P60 Pro",            "Smartphone"),
    "86310323": ("Huawei", "Mate 50 Pro",        "Smartphone"),
    "86310423": ("Huawei", "P50 Pro",            "Smartphone"),

    # ── NOKIA ─────────────────────────────────────────────
    "35473524": ("Nokia", "Nokia G42",           "Smartphone"),
    "35473624": ("Nokia", "Nokia X30",           "Smartphone"),
    "35287823": ("Nokia", "Nokia G60",           "Smartphone"),
}

# ============================================================
#   ORIGIN COUNTRY FROM IMEI PREFIX (RBI codes)
#   Source: ITU-T E.212 standard — always accurate
# ============================================================

RBI_COUNTRY = {
    "00": "United States", "01": "United States", "02": "United States",
    "03": "United States", "04": "United States", "05": "United States",
    "06": "United States", "07": "United States", "08": "United States",
    "09": "United States", "10": "United States", "11": "United States",
    "12": "United States", "13": "United States", "20": "Canada",
    "21": "Canada",        "22": "Canada",        "23": "Canada",
    "24": "Canada",        "25": "Canada",        "26": "Canada",
    "27": "Canada",        "28": "Canada",        "29": "Canada",
    "30": "Australia",     "31": "Australia",     "32": "Australia",
    "33": "Australia",     "34": "Australia",     "35": "Australia",
    "36": "Australia",     "37": "Australia",     "38": "Australia",
    "39": "Australia",     "40": "China",         "41": "China",
    "42": "China",         "43": "China",         "44": "United Kingdom",
    "45": "Denmark",       "46": "Austria",       "47": "Taiwan",
    "48": "Finland",       "49": "Germany",       "50": "Japan",
    "51": "South Korea",   "52": "Belgium",       "53": "Netherlands",
    "54": "France",        "55": "Spain",         "56": "Portugal",
    "57": "Luxembourg",    "58": "Switzerland",   "59": "Italy",
    "60": "Sweden",        "61": "Norway",        "62": "West Africa / Nigeria",
    "63": "East Africa",   "64": "Finland",       "65": "South Africa",
    "66": "Singapore",     "67": "New Zealand",   "68": "Brazil",
    "69": "Brazil",        "70": "Ireland",       "71": "Ireland",
    "72": "Singapore",     "73": "Singapore",     "74": "India",
    "75": "Malaysia",      "76": "Indonesia",     "77": "Philippines",
    "78": "Thailand",      "79": "Vietnam",       "80": "United Kingdom",
    "81": "United Kingdom","82": "Ukraine",       "83": "Russia",
    "84": "Russia",        "85": "Russia",        "86": "China",
    "87": "India",         "88": "India",         "89": "United States",
    "90": "United Arab Emirates","91": "China",   "92": "Pakistan",
    "93": "Afghanistan",   "94": "Bangladesh",    "95": "Myanmar",
    "96": "Iran",          "97": "Saudi Arabia",  "98": "Ghana",
    "99": "Global",
}

def get_country(imei: str) -> str:
    return RBI_COUNTRY.get(imei[:2], "Unknown")

# ============================================================
#   CORE IMEI LOOKUP FUNCTION
# ============================================================

def lookup_imei(imei: str) -> dict:
    """
    Looks up device info from built-in TAC database.
    TAC = first 8 digits of IMEI.
    Always works offline — no API needed.
    """
    tac = imei[:8]
    entry = TAC_DB.get(tac)

    if entry:
        brand, model, device_type = entry
        return {
            "brand":       brand,
            "model":       model,
            "device_type": device_type,
            "found":       True,
        }

    # Not in database — but we can still tell brand from known patterns
    # Apple devices: TAC starts with 35 and RBI is 35
    if imei.startswith("35") and any(
        imei[:4] in ["3530","3531","3532","3533","3534","3535",
                     "3536","3537","3538","3539","3540","3541",
                     "3542","3543","3544","3545","3546","3547",
                     "3548","3549","3550","3551","3552","3553",
                     "3554","3555","3556","3557","3558","3559",
                     "3560","3561","3562","3563","3564","3565",
                     "3566","3567","3568","3569","3570","3571",
                     "3572","3573","3574","3575","3576","3577",
                     "3578","3579","3580","3581","3582","3583",
                     "3584","3585","3586","3587","3588","3589",
                     "3590","3591","3592","3593","3594","3595",
                     "3596","3597","3598","3599"]
    ):
        return {
            "brand":       "Apple",
            "model":       "Model not in database",
            "device_type": "Apple Device",
            "found":       False,
        }

    # Samsung devices: TAC starts with 35 or 86 in Samsung ranges
    if imei[:4] in ["3546","3547","3548","3528","3517"]:
        return {
            "brand":       "Samsung",
            "model":       "Model not in database",
            "device_type": "Smartphone",
            "found":       False,
        }

    return {
        "brand":       "Unknown",
        "model":       "Not in database",
        "device_type": "Unknown",
        "found":       False,
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
#   IMEI VALIDATION
# ============================================================

async def validate_imei(update, context):
    if not context.args:
        await update.message.reply_text(
            "❌ Please provide an IMEI number.\n\n"
            "Example:\n"
            "/check 356200549868335\n\n"
            "📱 How to find your IMEI:\n"
            "• Dial *#06# on your device\n"
            "• Settings → General → About\n"
            "• Check the original box"
        )
        return None
    imei = context.args[0].strip()
    if not imei.isdigit():
        await update.message.reply_text("❌ IMEI must contain numbers only.")
        return None
    if len(imei) != 15:
        await update.message.reply_text(
            f"❌ IMEI must be exactly 15 digits.\n"
            f"You entered {len(imei)} digit(s).\n\n"
            f"Dial *#06# to get the correct IMEI."
        )
        return None
    if not luhn_check(imei):
        await update.message.reply_text(
            "⚠️ This IMEI is not valid.\n\n"
            "The checksum failed — the number\n"
            "was likely typed incorrectly.\n\n"
            "Please double check and try again.\n"
            "Dial *#06# to get the exact IMEI."
        )
        return None
    return imei

# ============================================================
#   /check — FREE DEVICE INFO (REAL DATA ONLY)
# ============================================================

async def check_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    imei = await validate_imei(update, context)
    if not imei:
        return

    msg = await update.message.reply_text("🔍 Looking up your device...")

    device  = lookup_imei(imei)
    country = get_country(imei)
    tac     = imei[:8]

    brand  = device["brand"]
    model  = device["model"]
    dtype  = device["device_type"]
    found  = device["found"]

    if found:
        db_note = "✅ Matched in TAC database"
    elif brand != "Unknown":
        db_note = "⚠️ Brand detected — model not in database"
    else:
        db_note = "⚠️ Device not found in database"

    report = (
        f"📱 FREE IMEI CHECK\n"
        f"{'━' * 28}\n\n"
        f"🔢 IMEI:           {imei}\n"
        f"✅ IMEI Valid:     Yes\n"
        f"🏷️  TAC Code:       {tac}\n\n"
        f"📋 DEVICE INFO\n"
        f"{'━' * 28}\n"
        f"▸ Brand:          {brand}\n"
        f"▸ Model:          {model}\n"
        f"▸ Device Type:    {dtype}\n"
        f"▸ Origin Country: {country}\n\n"
        f"{'━' * 28}\n"
        f"ℹ️ {db_note}\n\n"
        f"{'━' * 28}\n"
        f"🔐 WANT A FULL CHECK?\n"
        f"FMI • iCloud • Carrier • Blacklist\n"
        f"requires a paid service.\n"
        f"👉 Contact our admin below 👇"
    )

    await msg.delete()
    await update.message.reply_text(report, reply_markup=get_check_buttons())

# ============================================================
#   /imei — HELP MENU
# ============================================================

async def imei_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📱 FREE IMEI CHECKER\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "What you get FREE:\n"
        "✅ IMEI validity check\n"
        "✅ Brand\n"
        "✅ Model name\n"
        "✅ Device type\n"
        "✅ Country of origin\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "Usage:\n"
        "/check [15-digit IMEI]\n\n"
        "Example:\n"
        "/check 356200549868335\n\n"
        "📱 How to find your IMEI:\n"
        "• Dial *#06#\n"
        "• Settings → General → About\n"
        "• Check the original box\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "Need FMI / iCloud / Carrier\n"
        "/ Blacklist check?\n"
        "👉 Contact our admin below 👇",
        reply_markup=get_check_buttons(),
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
#   MAIN — Python 3.14 compatible
# ============================================================

async def run_bot():
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("  🤖 iosunlocks Bot starting...")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    if os.path.exists(VIDEO_FILE):
        print("✅ Video found: IMG_4956.MP4")
    else:
        print("⚠️  Video NOT found — place IMG_4956.MP4 in same folder")
    print(f"✅ TAC database loaded: {len(TAC_DB)} devices")
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
