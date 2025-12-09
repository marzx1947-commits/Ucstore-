# ucstore_variant_a.py — Full UCstore bot (Variant A)
# Changes (Variant A):
# - Phone requested first; after phone the bot asks for language.
# - Main menu uses keyboard buttons that send bot commands (e.g. /catalog, /cart, /wishlist, /info).
# - Added /language command to change language (shows inline language buttons).
# - Improved user profile display (masked phone, username, last game id from last order, cart summary).
# - Kept original labels and flows where possible.
#
# Requirements: python-telegram-bot v20+, Python 3.10+
# NOTE: Replace TOKEN with your bot token before running.

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
import datetime
import json
import os
import random
import string
from typing import Dict, Any

# -------------------- CONFIG --------------------
TOKEN = "8524676045:AAHXHO6tYovrMAAGxAQZUi2Z-TGFBUPeMyY"  # <-- set your bot token
ADMIN_IDS = [8436218638]  # set admin Telegram IDs here
USERS_FILE = "users.json"
ORDERS_FILE = "orders.json"

# payment recipients / examples
VISA_NUMBER = "4439200020432471"
SBER_NUMBER = "2202208496090011"
FREE_UC_CHANNEL = "@marzbon_media"  # channel to require subscription for some free UC

# -------------------- CATALOG (names intentionally NOT translated) --------------------
ITEMS = {
    1: {"name": "60 UC", "price": 10},
    2: {"name": "325 UC", "price": 50},
    3: {"name": "660 UC", "price": 100},
    4: {"name": "1800 UC", "price": 250},
    5: {"name": "3850 UC", "price": 500},
    6: {"name": "8100 UC", "price": 1000},
}

# -------------------- LONG INFO (user-provided) --------------------
INFO_TEXT_TG = """UCstore — ин боти расмии фурӯши UC барои PUBG Mobile ва дигар хидматҳои рақамии бозӣ мебошад. Мо барои бозингарони тоҷик платформаи боэътимод, босифат ва осонро фароҳам овардаем, то харид кардан осон, бехатар ва зуд сурат гирад. ⚡️

🔹 Афзалиятҳои UCstore:

🎁 UC-и ройгон 

🫴 Мо ба шумо ҳаррӯз аз 1 то 5 uc-и ройгон медиҳем ва инчунин бо даъвати ҳар як дуст шумо 2 uc ба даст меоред.

• 🛍 Каталоги пурра бо нархҳои дастрас
• 💳 Усулҳои гуногуни пардохт (аз ҷумла роҳи нави корти милли ва  VISA)
• ⚙️ Системаи автоматии фармоиш ва тасдиқ
• 💬 Пуштибонии зуд аз ҷониби админ
• ❤️ Имкони илова ба “дилхоҳҳо” ва сабади шахсӣ
• 🔔 Огоҳии фаврӣ дар бораи ҳолати фармоиш

📦 Чӣ тавр кор мекунад:
1️⃣ Ба бот ворид шавед
2️⃣ Маҳсулоти дилхоҳатонро интихоб кунед
3️⃣ Фармоиш диҳед ва пардохтро анҷом диҳед
4️⃣ Мунтазир шавед — UC ба ҳисоби шумо фиристода мешавад 🎁

🤝 Бартарии мо — шаффофият, суръат ва эътимод.
Ҳар як фармоиш боэҳтиёт санҷида мешавад, то мизоҷон таҷрибаи беҳтарин гиранд.

Бо UCstore шумо ҳамеша бехатар, зуд ва бо эътимод харид мекунед 💪

Инчунин дар бораи тамоми мушкилот шумо ҳамеша метавонед ба админ тамос гиред @MARZBON_TJ
"""

# -------------------- LANGUAGES & TRANSLATIONS --------------------
LANGS = ["tg", "ru", "en", "fa"]
LANGUAGE_LABELS = {
    "tg": "Тоҷикӣ",
    "ru": "Русский",
    "en": "English",
    "fa": "فارسی",
}

TEXTS: Dict[str, Dict[str, str]] = {
    "ask_language": {
        "tg": "Лутфан забони худро интихоб кунед:",
        "ru": "Пожалуйста, выберите язык:",
        "en": "Please choose your language:",
        "fa": "لطفاً زبان خود را انتخاب کنید:",
    },
    "ask_phone": {
        "tg": "📱 Лутфан рақами телефони худро фиристед.",
        "ru": "📱 Пожалуйста, отправьте свой номер телефона.",
        "en": "📱 Please send your phone number.",
        "fa": "📱 لطفاً شماره تلفن خود را ارسال کنید.",
    },
    "btn_phone": {
        "tg": "📱 Рақам фиристодан",
        "ru": "📱 Отправить номер",
        "en": "📱 Send phone number",
        "fa": "📱 ارسال شماره",
    },
    "phone_ok": {
        "tg": "✅ Рақам қабул шуд! Шумо сабт шудед.",
        "ru": "✅ Номер получен! Вы зарегистрированы.",
        "en": "✅ Phone number received! You are registered.",
        "fa": "✅ شماره دریافت شد! شما ثبت شدید.",
    },
    "already_registered": {
        "tg": "👋 Салом, {}!",
        "ru": "👋 Привет, {}!",
        "en": "👋 Hello, {}!",
        "fa": "👋 سلام، {}!",
    },
    "registered_success": {
        "tg": "✅ Шумо бо муваффақият сабт шудед!!\n🔑 Код шумо: {code}",
        "ru": "✅ Вы успешно зарегистрированы!!\n🔑 Ваш код: {code}",
        "en": "✅ You have been successfully registered!!\n🔑 Your code: {code}",
        "fa": "✅ با موفقیت ثبت شدید!!\n🔑 کد شما: {code}",
    },
    "main_menu_title": {
        "tg": "Менюи асосӣ:",
        "ru": "Главное меню:",
        "en": "Main menu:",
        "fa": "منوی اصلی:",
    },
    "btn_catalog": {"tg": "🛍 Каталог", "ru": "🛍 Каталог", "en": "🛍 Catalog", "fa": "🛍 کاتالوگ"},
    "btn_wishlist": {"tg": "❤️ Дилхоҳҳо", "ru": "❤️ Избранное", "en": "❤️ Wishlist", "fa": "❤️ علاقه‌مندی‌ها"},
    "btn_cart": {"tg": "🛒 Сабад", "ru": "🛒 Корзина", "en": "🛒 Cart", "fa": "🛒 سبد"},
    "btn_admin_profile": {"tg": "💬 Профили админ", "ru": "💬 Профиль админа", "en": "💬 Admin profile", "fa": "💬 پروفایل ادمین"},
    "btn_info": {"tg": "ℹ Маълумот", "ru": "ℹ Информация", "en": "ℹ Info", "fa": "ℹ اطلاعات"},
    "btn_free_uc": {"tg": "🎁 UC ройгон", "ru": "🎁 Бесплатные UC", "en": "🎁 Free UC", "fa": "🎁 UC رایگان"},
    "btn_language": {"tg": "🌐 Забон", "ru": "🌐 Язык", "en": "🌐 Language", "fa": "🌐 زبان"},
    "btn_admin_panel": {"tg": "👑 Панели админ", "ru": "👑 Панель администратора", "en": "👑 Admin panel", "fa": "👑 پنل ادمین"},
    "catalog_title": {"tg": "🛍 Каталог:", "ru": "🛍 Каталог:", "en": "🛍 Catalog:", "fa": "🛍 کاتالوگ:"},
    "cart_empty": {"tg": "🛒 Сабад холист.", "ru": "🛒 Корзина пуста.", "en": "🛒 Your cart is empty.", "fa": "🛒 سبد خالی است."},
    "wishlist_empty": {"tg": "❤️ Дилхоҳҳо холист.", "ru": "❤️ Избранное пусто.", "en": "❤️ Wishlist is empty.", "fa": "❤️ لیست علاقه‌مندی خالی است."},
    "ask_game_id": {
        "tg": "🎮 Лутфан ID-и бозии худро ворид кунед (фақат рақамҳо):",
        "ru": "🎮 Пожалуйста, введите ваш игровой ID (только цифры):",
        "en": "🎮 Please enter your game ID (numbers only):",
        "fa": "🎮 لطفاً شناسه بازی خود را وارد کنید (فقط اعداد):",
    },
    "invalid_game_id": {
        "tg": "⚠️ Лутфан танҳо рақам ворид кунед (ID бояд рақам бошад).",
        "ru": "⚠️ Пожалуйста, вводите только цифры (ID должен быть числом).",
        "en": "⚠️ Please enter numbers only (ID must be numeric).",
        "fa": "⚠️ لطفاً فقط عدد وارد کنید (ID باید عدد باشد).",
    },
    "payment_choose": {
        "tg": "Лутфан тарзи пардохтро интихоб кунед:",
        "ru": "Пожалуйста, выберите способ оплаты:",
        "en": "Please choose a payment method:",
        "fa": "لطفاً روش پرداخت را انتخاب کنید:",
    },
    "send_proof": {
        "tg": "Пас аз пардохт, лутфан квитансияро ҳамчун акс ё файл ба ин чат фиристед.",
        "ru": "После оплаты, пожалуйста, отправьте квитанцию (скриншот) в этот чат.",
        "en": "After payment, please send the payment proof (screenshot) to this chat.",
        "fa": "پس از پرداخت، لطفاً رسید پرداخت را به صورت عکس یا فایل به این چت ارسال کنید.",
    },
    "proof_received": {
        "tg": "✅ Квитанция қабул шуд! Мунтазир шавед, то админ тасдиқ кунад.",
        "ru": "✅ Квитанция принята! Ожидайте подтверждения от админа.",
        "en": "✅ Proof received! Please wait for admin confirmation.",
        "fa": "✅ رسید دریافت شد! لطفاً منتظر تأیید ادمین باشید.",
    },
    "no_pending_order_proof": {
        "tg": "⚠️ Шумо ҳоло фармоиши интизори квитанция надоред.",
        "ru": "⚠️ У вас нет заказов, ожидающих квитанции.",
        "en": "⚠️ You don't have any orders awaiting proof.",
        "fa": "⚠️ شما سفارش منتظر رسید ندارید.",
    },
    "order_confirmed_user": {
        "tg": "✅ Пардохти шумо барои фармоиши №{order_id} тасдиқ шуд! Ташаккур.",
        "ru": "✅ Ваш платеж по заказу №{order_id} подтверждён! Спасибо.",
        "en": "✅ Your payment for order #{order_id} has been confirmed! Thank you.",
        "fa": "✅ پرداخت شما برای سفارش شماره {order_id} تأیید شد! متشکریم.",
    },
    "order_rejected_user": {
        "tg": "❌ Пардохти шумо барои фармоиши №{order_id} рад шуд. Лутфан бо админ тамос гиред.",
        "ru": "❌ Ваш платеж по заказу №{order_id} отклонён. Пожалуйста, свяжитесь с админом.",
        "en": "❌ Your payment for order #{order_id} was rejected. Please contact the admin.",
        "fa": "❌ پرداخت شما برای سفارش شماره {order_id} رد شد. لطفاً با ادمین تماس بگیرید.",
    },
    "broadcast_sent": {
        "tg": "✅ Паём ба {count} корбар фиристода шуд.",
        "ru": "✅ Сообщение отправлено {count} пользователям.",
        "en": "✅ Message sent to {count} users.",
        "fa": "✅ پیام به {count} کاربر ارسال شد.",
    },
    "error_generic": {
        "tg": "⚠️ Хато сурат гирифт. Лутфан дубора кӯшиш кунед.",
        "ru": "⚠️ Произошла ошибка. Повторите попытку.",
        "en": "⚠️ An error occurred. Please try again.",
        "fa": "⚠️ خطا رخ داد. لطفاً دوباره تلاش کنید.",
    },
    "invite_text": {
        "tg": "🔗 Ин линкро ба дӯстонат фирист:\n\n{invite}\n\nҲар дӯсте, ки сабт мешавад → ту 2 UC мегирӣ!",
        "ru": "🔗 Отправь эту ссылку друзьям:\n\n{invite}\n\nЗа каждого приглашённого — +2 UC!",
        "en": "🔗 Send this link to your friends:\n\n{invite}\n\nYou get +2 UC for each friend who registers!",
        "fa": "🔗 این لینک را برای دوستانتان ارسال کنید:\n\n{invite}\n\nبرای هر دوستی که ثبت‌نام کند +2 UC دریافت می‌کنید!",
    },
    "admin_panel_title": {"tg": "⚙️ Панели Администратор", "ru": "⚙️ Панель администратора", "en": "⚙️ Admin panel", "fa": "⚙️ پنل ادمین"},
    "users_list_title": {"tg": "📋 Рӯйхати корбарон:", "ru": "📋 Список пользователей:", "en": "📋 Users list:", "fa": "📋 لیست کاربران:"},
    "orders_list_title": {"tg": "📦 Рӯйхати заказҳо:", "ru": "📦 Список заказов:", "en": "📦 Orders list:", "fa": "📦 لیست سفارش‌ها:"},
    "confirm_deleted_wishlist": {"tg": "🗑️ Аз дилхоҳҳо ҳазф шуд!", "ru": "🗑️ Удалено из избранного!", "en": "🗑️ Removed from wishlist!", "fa": "🗑️ از علاقه‌مندی‌ها حذف شد!"},
    "info_text": {
        "tg": INFO_TEXT_TG,
        "ru": "ℹ Информация\n\nЭтот бот создан для покупки UC и услуг PUBG Mobile.",
        "en": "ℹ Info\n\nThis bot helps you buy UC and related PUBG Mobile services.",
        "fa": "ℹ اطلاعات\n\nاین ربات برای خرید UC و خدمات PUBG Mobile است.",
    },
}

# -------------------- Persistence helpers --------------------
def load_json(path: str, default: Any):
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return default
    return default


def save_json(path: str, data: Any):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def save_all():
    save_json(USERS_FILE, users_data)
    save_json(ORDERS_FILE, orders)


users_data = load_json(USERS_FILE, {})  # key: user_id -> user info
orders = load_json(ORDERS_FILE, [])  # list of orders

# runtime structures
user_carts: Dict[str, Dict[int, int]] = {}
user_wishlist: Dict[str, set] = {}
broadcast_mode: Dict[str, bool] = {}

# -------------------- Helpers --------------------
def generate_user_code(length: int = 6) -> str:
    chars = string.ascii_uppercase + string.digits
    return "".join(random.choice(chars) for _ in range(length))


def t(key: str, lang: str, **kwargs) -> str:
    if key not in TEXTS:
        return key
    entry = TEXTS[key]
    text = entry.get(lang) or entry.get("tg") or next(iter(entry.values()))
    if kwargs:
        try:
            return text.format(**kwargs)
        except Exception:
            return text
    return text


def get_menu_buttons_for_lang(lang: str):
    # Return ReplyKeyboardMarkup where each button sends a command (e.g. /catalog)
    # Labels are preserved per language.
    btns = [
        [KeyboardButton(f"/catalog") , KeyboardButton(f"/wishlist")],
        [KeyboardButton(f"/cart"), KeyboardButton(f"/profile")],
        [KeyboardButton(f"/info"), KeyboardButton(f"/free_uc")],
        [KeyboardButton(f"/language")],
    ]
    # If admin, add admin panel button as a command
    return ReplyKeyboardMarkup(btns, resize_keyboard=True, one_time_keyboard=False)


# -------------------- /start --------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
    user = update.message.from_user
    user_id = str(user.id)

    # If registered and phone present -> show menu
    if user_id in users_data and users_data[user_id].get("phone"):
        lang = users_data[user_id].get("lang", "tg")
        await update.message.reply_text(t("already_registered", lang).format(user.first_name))
        await show_main_menu(update.message.chat, user_id)
        return

    # If user exists without phone or new user -> ask phone first
    kb = ReplyKeyboardMarkup(
        [[KeyboardButton(t("btn_phone", "tg"), request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    await update.message.reply_text(t("ask_phone", "tg"), reply_markup=kb)


# -------------------- Contact handler (first-time phone) --------------------
async def contact_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact = update.message.contact
    if not contact:
        return
    user = update.message.from_user
    user_id = str(user.id)

    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if user_id not in users_data:
        # create user record with empty lang -> will ask language next
        users_data[user_id] = {
            "id": int(user_id),
            "name": user.first_name or "",
            "username": user.username or "",
            "phone": contact.phone_number,
            "date": now_str,
            "free_uc": 0,
            "last_claim": None,
            "last_daily_uc": None,
            "code": generate_user_code(),
            "lang": "",  # empty until language chosen
        }
    else:
        users_data[user_id]["phone"] = contact.phone_number
        # preserve existing lang if present
    save_all()

    # notify admins about new registration (optional)
    try:
        for admin in ADMIN_IDS:
            context.bot.send_message(
                admin,
                f"👤 New user: {user.first_name} ({user.username or '—'})\n📱 {contact.phone_number}\n🔑 Code: {users_data[user_id]['code']}"
            )
    except Exception:
        pass

    # reply and ask language selection (inline)
    await update.message.reply_text(t("phone_ok", "tg"), reply_markup=ReplyKeyboardRemove())
    # show language inline selection
    buttons = []
    row = []
    for code, label in LANGUAGE_LABELS.items():
        row.append(InlineKeyboardButton(label, callback_data=f"setlang_change_{code}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    await update.message.reply_text(t("ask_language", "tg"), reply_markup=InlineKeyboardMarkup(buttons))


# -------------------- Language callback --------------------
async def set_language_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data or ""
    user = query.from_user
    user_id = str(user.id)

    # If changing language for existing user (or after phone)
    if data.startswith("setlang_change_"):
        code = data.split("setlang_change_", 1)[1]
        if user_id in users_data:
            users_data[user_id]["lang"] = code
            save_all()
            await query.message.reply_text(f"✔ {LANGUAGE_LABELS.get(code, code)} — {t('main_menu_title', code)}")
            await show_main_menu(query.message.chat, user_id)
            return

    await query.message.reply_text(t("error_generic", "tg"))


# -------------------- Show main menu --------------------
async def show_main_menu(chat, user_id: str):
    lang = users_data.get(user_id, {}).get("lang", "tg") or "tg"
    kb = get_menu_buttons_for_lang(lang)
    # admin button appears only for admin users — since we use command keyboard, admin can use /adminpanel
    await chat.send_message(t("main_menu_title", lang), reply_markup=kb)


# -------------------- Catalog handlers --------------------
async def catalog_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target = update.message or (update.callback_query and update.callback_query.message)
    if not target:
        return
    from_user = update.message.from_user if update.message else update.callback_query.from_user
    lang = users_data.get(str(from_user.id), {}).get("lang", "tg") or "tg"

    buttons = []
    row = []
    for i, item in ITEMS.items():
        row.append(InlineKeyboardButton(f"{item['name']} — {item['price']} TJS", callback_data=f"select_{i}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    back_label = {"tg":"Бозгашт","ru":"Назад","en":"Back","fa":"بازگашт"}[lang]
    buttons.append([InlineKeyboardButton("⬅️ " + back_label, callback_data="back_main")])

    await target.reply_text(t("catalog_title", lang), reply_markup=InlineKeyboardMarkup(buttons))


async def select_item_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    try:
        item_id = int(query.data.split("_")[1])
    except Exception:
        await query.message.reply_text(t("error_generic", "tg"))
        return

    item = ITEMS.get(item_id)
    if not item:
        await query.message.reply_text(t("error_generic", "tg"))
        return

    user_lang = users_data.get(str(query.from_user.id), {}).get("lang", "tg") or "tg"
    add_label = {"tg":"Илова ба сабад","ru":"В корзину","en":"Add to cart","fa":"افزودن به سبد"}[user_lang]
    wish_label = {"tg":"Ба дилхоҳҳо","ru":"В избранное","en":"To wishlist","fa":"به علاقه‌مندی‌ها"}[user_lang]
    back_label = {"tg":"Бозгашт","ru":"Назад","en":"Back","fa":"بازгашт"}[user_lang]

    buttons = [
        [InlineKeyboardButton("🛒 " + add_label, callback_data=f"addcart_{item_id}"),
         InlineKeyboardButton("❤️ " + wish_label, callback_data=f"addwish_{item_id}")],
        [InlineKeyboardButton("⬅️ " + back_label, callback_data="back_main")],
    ]
    await query.message.reply_text(f"🛍 {item['name']} — {item['price']} TJS", reply_markup=InlineKeyboardMarkup(buttons))


async def addcart_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)
    try:
        item_id = int(query.data.split("_")[1])
    except Exception:
        return
    user_carts.setdefault(user_id, {})
    user_carts[user_id][item_id] = user_carts[user_id].get(item_id, 0) + 1
    lang = users_data.get(user_id, {}).get("lang", "tg") or "tg"
    await query.message.reply_text({"tg":"✅ Ба сабад илова шуд!","ru":"✅ Добавлено в корзину!","en":"✅ Added to cart!","fa":"✅ به سبد اضافه شد!"}[lang])


async def addwish_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)
    try:
        item_id = int(query.data.split("_")[1])
    except Exception:
        return
    user_wishlist.setdefault(user_id, set()).add(item_id)
    lang = users_data.get(user_id, {}).get("lang", "tg") or "tg"
    await query.message.reply_text({"tg":"❤️ Ба дилхоҳҳо илova шуд!","ru":"❤️ Добавлено в избранное!","en":"❤️ Added to wishlist!","fa":"❤️ به علاقه‌مندی اضافه شد!"}[lang])


async def open_wishlist_from_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    wishlist = user_wishlist.get(user_id, set())
    lang = users_data.get(user_id, {}).get("lang", "tg") or "tg"
    if not wishlist:
        await update.message.reply_text(t("wishlist_empty", lang))
        return

    for i in list(wishlist):
        item = ITEMS.get(i)
        if not item:
            continue
        add_label = {"tg":"Ба сабад","ru":"В корзину","en":"Add to cart","fa":"افزودن به سبد"}[lang]
        rem_label = {"tg":"Хок кардан","ru":"Удалить","en":"Remove","fa":"حذف"}[lang]
        buttons = [
            [InlineKeyboardButton("🛒 " + add_label, callback_data=f"addcart_{i}"),
             InlineKeyboardButton("🗑️ " + rem_label, callback_data=f"removewish_{i}")]
        ]
        await update.message.reply_text(f"❤️ {item['name']} — {item['price']} TJS", reply_markup=InlineKeyboardMarkup(buttons))


async def removewish_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)
    try:
        item_id = int(query.data.split("_")[1])
    except Exception:
        return
    if user_id in user_wishlist:
        user_wishlist[user_id].discard(item_id)
    lang = users_data.get(user_id, {}).get("lang", "tg") or "tg"
    await query.message.reply_text(t("confirm_deleted_wishlist", lang))


# -------------------- Cart & Checkout --------------------
async def show_cart_from_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    cart = user_carts.get(user_id, {})
    lang = users_data.get(user_id, {}).get("lang", "tg") or "tg"
    if not cart:
        await update.message.reply_text(t("cart_empty", lang))
        return

    intro = {"tg":"🛍 Маҳсулоти шумо:\n","ru":"🛍 Ваши товары:\n","en":"🛍 Your items:\n","fa":"🛍 موارد شما:\n"}[lang]
    text = intro
    total = 0
    for i, qty in cart.items():
        item = ITEMS.get(i)
        if not item:
            continue
        subtotal = item["price"] * qty
        total += subtotal
        text += f"- {item['name']} x{qty} = {subtotal} TJS\n"
    total_label = {"tg":"Ҳамагӣ:","ru":"Итого:","en":"Total:","fa":"جمع:"}[lang]
    text += f"\n💰 {total_label} {total} TJS"

    place_label = {"tg":"Фармоиш додан","ru":"Оформить заказ","en":"Place order","fa":"ثبت سفارش"}[lang]
    clear_label = {"tg":"Пок кардан","ru":"Очистить","en":"Clear","fa":"پاک کردن"}[lang]
    back_label = {"tg":"Бозгашт","ru":"Назад","en":"Back","fa":"بازгашт"}[lang]

    buttons = [
        [InlineKeyboardButton("📦 " + place_label, callback_data="checkout"),
         InlineKeyboardButton("🗑️ " + clear_label, callback_data="clear_cart")],
        [InlineKeyboardButton("⬅️ " + back_label, callback_data="back_main")],
    ]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons))


async def clear_cart_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)
    user_carts[user_id] = {}
    lang = users_data.get(user_id, {}).get("lang", "tg") or "tg"
    await query.message.reply_text({"tg":"🧹 Сабад тоза шуд!","ru":"🧹 Корзина очищена!","en":"🧹 Cart cleared!","fa":"🧹 سبد پاک شد!"}[lang])


async def checkout_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)
    cart = user_carts.get(user_id, {})
    lang = users_data.get(user_id, {}).get("lang", "tg") or "tg"
    if not cart:
        await query.message.reply_text(t("cart_empty", lang))
        return

    await query.message.reply_text(t("ask_game_id", lang))
    context.user_data["awaiting_game_id"] = True
    context.user_data["pending_order_total"] = sum(ITEMS[i]["price"] * q for i, q in cart.items())


async def get_game_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("awaiting_game_id"):
        return
    game_id = update.message.text.strip()
    lang = users_data.get(str(update.message.from_user.id), {}).get("lang", "tg") or "tg"
    if not game_id.isdigit():
        await update.message.reply_text(t("invalid_game_id", lang))
        return

    context.user_data["awaiting_game_id"] = False
    user_id = str(update.message.from_user.id)
    total = context.user_data.pop("pending_order_total", 0)

    order = _create_order_record(user_id, total)
    order["game_id"] = game_id
    order["status"] = "choose_payment"
    save_all()

    buttons = [
        [InlineKeyboardButton("💳 VISA", callback_data=f"pay_visa_{order['id']}")],
        [InlineKeyboardButton("🏦 SberBank", callback_data=f"pay_sber_{order['id']}")],
    ]
    await update.message.reply_text(
        f"Фармоиш №{order['id']} \n🎮 ID: {game_id}\n💰 {total} TJS\n\n" + t("payment_choose", lang),
        reply_markup=InlineKeyboardMarkup(buttons)
    )


# -------------------- Payment method selection --------------------
async def payment_method_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    parts = data.split("_")
    if len(parts) < 3:
        await query.message.reply_text(t("error_generic", "tg"))
        return

    method = parts[1]
    try:
        order_id = int(parts[2])
    except Exception:
        await query.message.reply_text(t("error_generic", "tg"))
        return

    if method == "visa":
        card = VISA_NUMBER
        method_name = "VISA"
    else:
        card = SBER_NUMBER
        method_name = "SberBank"

    for order in orders:
        if order["id"] == order_id:
            order["status"] = "awaiting_proof"
            order["payment_method"] = method_name
            save_all()
            lang = users_data.get(str(query.from_user.id), {}).get("lang", "tg") or "tg"
            await query.message.reply_text(f"💳 {method_name}\n📌 {card}\n\n" + t("send_proof", lang))
            return

    await query.message.reply_text(t("error_generic", "tg"))


# -------------------- Receive payment proof --------------------
async def receive_payment_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    # find last order awaiting proof for this user
    order = None
    for o in reversed(orders):
        if str(o.get("user_id")) == user_id and o.get("status") == "awaiting_proof":
            order = o
            break
    if not order:
        lang = users_data.get(user_id, {}).get("lang", "tg") or "tg"
        await update.message.reply_text(t("no_pending_order_proof", lang))
        return

    file_id = None
    is_photo = False
    if update.message.photo:
        file_id = update.message.photo[-1].file_id
        is_photo = True
    elif update.message.document:
        file_id = update.message.document.file_id
        is_photo = False
    else:
        lang = users_data.get(user_id, {}).get("lang", "tg") or "tg"
        await update.message.reply_text(t("error_generic", lang))
        return

    order["status"] = "proof_sent"
    order["proof_file"] = file_id
    save_all()

    caption = (
        f"📦 Order #{order['id']}\n"
        f"👤 @{order.get('username') or order.get('user_name')}\n"
        f"🎮 ID: {order.get('game_id')}\n"
        f"💰 {order.get('total')} TJS\n"
        f"💳 {order.get('payment_method')}\n"
        f"📱 {order.get('phone') or '—'}\n"
        f"🕒 {order.get('time')}"
    )

    buttons = [
        [
            InlineKeyboardButton("✅ Confirm", callback_data=f"pay_confirm_{order['id']}"),
            InlineKeyboardButton("❌ Reject", callback_data=f"pay_reject_{order['id']}"),
        ]
    ]

    for admin in ADMIN_IDS:
        try:
            if is_photo:
                await context.bot.send_photo(chat_id=admin, photo=file_id, caption=caption, reply_markup=InlineKeyboardMarkup(buttons))
            else:
                await context.bot.send_document(chat_id=admin, document=file_id, caption=caption, reply_markup=InlineKeyboardMarkup(buttons))
        except Exception:
            pass

    lang = users_data.get(user_id, {}).get("lang", "tg") or "tg"
    await update.message.reply_text(t("proof_received", lang))


# -------------------- Admin verify payment --------------------
async def admin_payment_verify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    parts = query.data.split("_")
    if len(parts) < 3:
        await query.message.reply_text(t("error_generic", "tg"))
        return
    action = parts[1]
    try:
        order_id = int(parts[2])
    except Exception:
        await query.message.reply_text(t("error_generic", "tg"))
        return

    for order in orders:
        if order["id"] == order_id:
            user_chat = int(order["user_id"])
            if action == "confirm":
                order["status"] = "confirmed"
                save_all()
                try:
                    lang = users_data.get(str(user_chat), {}).get("lang", "tg") or "tg"
                    await context.bot.send_message(user_chat, t("order_confirmed_user", lang).format(order_id=order_id))
                except Exception:
                    pass
                await query.message.reply_text("✅ Confirmed.")
            else:
                order["status"] = "rejected"
                save_all()
                try:
                    lang = users_data.get(str(user_chat), {}).get("lang", "tg") or "tg"
                    await context.bot.send_message(user_chat, t("order_rejected_user", lang).format(order_id=order_id))
                except Exception:
                    pass
                await query.message.reply_text("❌ Rejected.")
            return
    await query.message.reply_text(t("error_generic", "tg"))


# -------------------- Free UC system --------------------
async def free_uc_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.message.chat if update.message else update.callback_query.message.chat
    from_user = update.message.from_user if update.message else update.callback_query.from_user
    user_id = str(from_user.id)
    lang = users_data.get(user_id, {}).get("lang", "tg") or "tg"

    if user_id not in users_data:
        await chat.send_message(t("error_generic", lang))
        return

    # Check subscription (best-effort)
    subscribed = False
    try:
        member = await context.bot.get_chat_member(FREE_UC_CHANNEL, int(user_id))
        subscribed = member.status in ["member", "administrator", "creator"]
    except Exception:
        subscribed = False

    buttons = []
    if subscribed:
        daily_label = {"tg":"🎲 Гирифтани UC-и рӯзона","ru":"🎲 Ежедневный UC","en":"🎲 Daily UC","fa":"🎲 UC روزانه"}[lang]
        my_label = {"tg":"📊 UC-и ҷамъшуда","ru":"📊 Накопленные UC","en":"📊 Your UC balance","fa":"📊 موجودی UC"}[lang]
        buttons.append([InlineKeyboardButton(daily_label, callback_data="daily_uc")])
        buttons.append([InlineKeyboardButton(my_label, callback_data="my_uc")])
        buttons.append([InlineKeyboardButton({"tg":"🎁 60 UC","ru":"🎁 60 UC","en":"🎁 60 UC","fa":"🎁 60 UC"}[lang], callback_data="claim_60"),
                         InlineKeyboardButton({"tg":"🎁 325 UC","ru":"🎁 325 UC","en":"🎁 325 UC","fa":"🎁 325 UC"}[lang], callback_data="claim_325")])
    else:
        channel_url = f"https://t.me/{FREE_UC_CHANNEL.lstrip('@')}"
        sub_label = {"tg":"📢 Обуна шудан","ru":"📢 Подписаться","en":"📢 Subscribe","fa":"📢 اشتراک"}[lang]
        check_label = {"tg":"🔄 Санҷиш","ru":"🔄 Проверить","en":"🔄 Check","fa":"🔄 بررسی"}[lang]
        buttons.append([InlineKeyboardButton(sub_label, url=channel_url)])
        buttons.append([InlineKeyboardButton(check_label, callback_data="check_sub_ucfree")])

    invite_label = {"tg":"🔗 Даъвати дӯстон","ru":"🔗 Пригласить","en":"🔗 Invite friends","fa":"🔗 دعوت"}[lang]
    buttons.append([InlineKeyboardButton(invite_label, callback_data="invite_link")])

    free_title = {"tg":"🎁 Менюи UC ройгон:","ru":"🎁 Меню бесплатных UC:","en":"🎁 Free UC menu:","fa":"🎁 منوی UC رایگان:"}[lang]
    await chat.send_message(free_title, reply_markup=InlineKeyboardMarkup(buttons))


async def check_sub_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    await free_uc_menu(update, context)


async def daily_uc_roll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    user_id = str(q.from_user.id)
    lang = users_data.get(user_id, {}).get("lang", "tg") or "tg"
    user = users_data.get(user_id)
    if not user:
        await q.message.reply_text(t("error_generic", lang))
        return

    now = datetime.datetime.now()
    last = user.get("last_daily_uc")
    if last:
        try:
            last_dt = datetime.datetime.strptime(last, "%Y-%m-%d %H:%M:%S")
            if (now - last_dt).total_seconds() < 24 * 3600:
                remaining = int((24 * 3600 - (now - last_dt).total_seconds()) // 3600)
                msg = {"tg":f"⏳ Шумо аллакай UC гирифтед. Ба шумо боз {remaining} соат мондааст.","ru":f"⏳ Вы уже получили UC. Остаётся {remaining} часов.","en":f"⏳ You've already claimed UC. {remaining} hours remaining.","fa":f"⏳ شما قبلاً UC دریافت کرده‌اید. {remaining} ساعت مانده است."}[lang]
                await q.message.reply_text(msg)
                return
        except Exception:
            pass

    roll = random.choices([1,2,3,4,5], weights=[70,20,7,2,1])[0]
    user["free_uc"] = user.get("free_uc", 0) + roll
    user["last_daily_uc"] = now.strftime("%Y-%m-%d %H:%M:%S")
    users_data[user_id] = user
    save_all()
    await q.message.reply_text({"tg":f"🎉 Шумо {roll} UC гирифтед!\n📊 Ҳамагӣ: {user['free_uc']} UC","ru":f"🎉 Вы получили {roll} UC!\n📊 Всего: {user['free_uc']} UC","en":f"🎉 You received {roll} UC!\n📊 Total: {user['free_uc']} UC","fa":f"🎉 شما {roll} UC دریافت کردید!\n📊 مجموع: {user['free_uc']} UC"}[lang])


async def my_uc_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    user_id = str(q.from_user.id)
    lang = users_data.get(user_id, {}).get("lang", "tg") or "tg"
    user = users_data.get(user_id, {})
    amount = user.get("free_uc", 0)
    btns = [
        [InlineKeyboardButton({"tg":"🎁 60 UC","ru":"🎁 60 UC","en":"🎁 60 UC","fa":"🎁 60 UC"}[lang], callback_data="claim_60")],
        [InlineKeyboardButton({"tg":"🎁 325 UC","ru":"🎁 325 UC","en":"🎁 325 UC","fa":"🎁 325 UC"}[lang], callback_data="claim_325")]
    ]
    await q.message.reply_text({"tg":f"📊 Шумо доред: {amount} UC","ru":f"📊 У вас: {amount} UC","en":f"📊 You have: {amount} UC","fa":f"📊 شما دارید: {amount} UC"}[lang], reply_markup=InlineKeyboardMarkup(btns))


async def claim_uc_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data
    needed = 60 if data == "claim_60" else 325 if data == "claim_325" else None
    user_id = str(q.from_user.id)
    lang = users_data.get(user_id, {}).get("lang", "tg") or "tg"
    if not needed:
        return
    user = users_data.get(user_id, {})
    if user.get("free_uc", 0) < needed:
        await q.message.reply_text({"tg":f"❌ Шумо UC кофӣ надоред. Шумо доред: {user.get('free_uc',0)} UC","ru":f"❌ У вас недостаточно UC. У вас: {user.get('free_uc',0)} UC","en":f"❌ You don't have enough UC. You have: {user.get('free_uc',0)} UC","fa":f"❌ UC کافی ندارید. شما دارید: {user.get('free_uc',0)} UC"}[lang])
        return
    context.user_data["awaiting_free_id"] = needed
    await q.message.reply_text({"tg":"🎮 Лутфан ID-и PUBG-ро ворид кунед (8–15 рақам):","ru":"🎮 Введите ваш PUBG ID (8–15 цифр):","en":"🎮 Enter your PUBG ID (8–15 digits):","fa":"🎮 شناسه PUBG خود را وارد کنید (8–15 عدد):"}[lang])


async def get_free_uc_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "awaiting_free_id" not in context.user_data:
        return
    ttext = update.message.text.strip()
    lang = users_data.get(str(update.message.from_user.id), {}).get("lang", "tg") or "tg"
    if not ttext.isdigit() or not (8 <= len(ttext) <= 15):
        await update.message.reply_text({"tg":"⚠️ Танҳо рақам, аз 8 то 15 рақам! Лутфан дубора кӯшиш кунед.","ru":"⚠️ Только цифры, от 8 до 15 цифр! Пожалуйста, повторите.","en":"⚠️ Numbers only, 8–15 digits. Please try again.","fa":"⚠️ فقط عدد، از 8 تا 15 رقم! لطفاً دوباره تلاش کنید."}[lang])
        return
    amount = context.user_data.pop("awaiting_free_id")
    user_id = str(update.message.from_user.id)
    user = users_data.get(user_id)
    if not user:
        await update.message.reply_text(t("error_generic", lang))
        return

    user["free_uc"] = max(0, user.get("free_uc", 0) - amount)
    users_data[user_id] = user
    save_all()

    order_id = random.randint(10000, 99999)
    order = {
        "id": order_id,
        "user_id": user_id,
        "username": user.get("username"),
        "phone": user.get("phone"),
        "total": 0,
        "type": "free_uc",
        "pack": amount,
        "game_id": ttext,
        "status": "pending",
        "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    orders.append(order)
    save_all()

    for admin in ADMIN_IDS:
        try:
            btn = InlineKeyboardMarkup([[InlineKeyboardButton("✅ Тасдиқ", callback_data=f"admin_confirm_free_{order_id}"), InlineKeyboardButton("❌ Рад", callback_data=f"admin_reject_free_{order_id}")]])
            await context.bot.send_message(admin, f"📦 Free UC order #{order_id}\n👤 @{order['username']}\n🎮 ID: {ttext}\n🎁 Pack: {amount} UC", reply_markup=btn)
        except Exception:
            pass

    await update.message.reply_text({"tg":f"🎁 Дархости {amount} UC ба админ фиристода шуд! (Фармоиш №{order_id})","ru":f"🎁 Запрос {amount} UC отправлен админу! (Заказ №{order_id})","en":f"🎁 Request for {amount} UC sent to admin! (Order #{order_id})","fa":f"🎁 درخواست {amount} UC به ادمین ارسال شد! (سفارش #{order_id})"}[lang])


async def admin_confirm_free(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    try:
        order_id = int(q.data.split("_")[-1])
    except Exception:
        return
    for o in orders:
        if o["id"] == order_id and o.get("type") == "free_uc":
            if o["status"] != "pending":
                await q.message.reply_text(f"Order already in state: {o['status']}")
                return
            o["status"] = "confirmed"
            save_all()
            try:
                await context.bot.send_message(int(o["user_id"]), "✅ Free UC request confirmed!")
            except Exception:
                pass
            await q.message.reply_text("✅ Confirmed.")
            return
    await q.message.reply_text("Order not found.")


async def admin_reject_free(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    try:
        order_id = int(q.data.split("_")[-1])
    except Exception:
        return
    for o in orders:
        if o["id"] == order_id and o.get("type") == "free_uc":
            o["status"] = "rejected"
            save_all()
            try:
                await context.bot.send_message(int(o["user_id"]), "❌ Free UC request rejected. Please contact admin.")
            except Exception:
                pass
            await q.message.reply_text("❌ Rejected.")
            return
    await q.message.reply_text("Order not found.")


# -------------------- Admin functions --------------------
async def admin_panel_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = str(query.from_user.id)
    lang = users_data.get(user_id, {}).get("lang", "tg") or "tg"

    if data == "admin_panel":
        keyboard = [
            [InlineKeyboardButton({"tg":"👤 Корбарон","ru":"👤 Пользователи","en":"👤 Users","fa":"👤 کاربران"}[lang], callback_data="admin_users")],
            [InlineKeyboardButton({"tg":"📦 Заказҳо","ru":"📦 Заказы","en":"📦 Orders","fa":"📦 سفارش‌ها"}[lang], callback_data="admin_orders")],
            [InlineKeyboardButton({"tg":"📢 Расонидани паём","ru":"📢 Трансляция","en":"📢 Broadcast","fa":"📢 پخش"}[lang], callback_data="admin_broadcast")],
            [InlineKeyboardButton({"tg":"⬅️ Бозгашт","ru":"⬅️ Назад","en":"⬅️ Back","fa":"⬅️ بازгашт"}[lang], callback_data="back_main")],
        ]
        await query.message.edit_text(t("admin_panel_title", lang), reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if data == "admin_users":
        if not users_data:
            text = {"tg":"📋 Ҳоло ҳеҷ корбар нест.","ru":"📋 Пока нет пользователей.","en":"📋 No users yet.","fa":"📋 هنوز کاربری ثبت نشده است."}[lang]
        else:
            text = t("users_list_title", lang) + "\n\n"
            for uid, u in users_data.items():
                text += f"• {u.get('name','—')} — {u.get('phone','—')} (id: {uid})\n"
        await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton({"tg":"⬅️ Бозгашт","ru":"⬅️ Назад","en":"⬅️ Back","fa":"⬅️ بازгашт"}[lang], callback_data="admin_panel")]]))
        return

    if data == "admin_orders":
        if not orders:
            text = {"tg":"❗ Ҳоло ҳеҷ заказ нест.","ru":"❗ Пока нет заказов.","en":"❗ No orders yet.","fa":"❗ هنوز سفارشی وجود ندارد."}[lang]
        else:
            text = t("orders_list_title", lang) + "\n\n"
            for o in orders:
                text += f"#{o['id']} — @{o.get('username') or o.get('user_name','-')} — {o.get('total', o.get('pack',0))} — {o['status']}\n"
        await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton({"tg":"⬅️ Бозгашт","ru":"⬅️ Назад","en":"⬅️ Back","fa":"⬅️ بازгашт"}[lang], callback_data="admin_panel")]]))
        return

    if data == "admin_broadcast":
        broadcast_mode[user_id] = True
        await query.message.edit_text({"tg":"✏️ Ҳозир матни паёмро навис — ман онро ба *ҳама корбарҳо* мефиристам.","ru":"✏️ Введите сообщение — я отправлю его всем пользователям.","en":"✏️ Send the message now — I'll deliver it to all users.","fa":"✏️ اکنون متن پیام را وارد کنید — من آن را به همه کاربران ارسال خواهم کرد."}[lang], parse_mode="Markdown")
        return


# -------------------- User profile display --------------------
def mask_phone(phone: str) -> str:
    if not phone:
        return "—"
    # show first 3 and last 2 digits with stars
    digits = "".join(ch for ch in phone if ch.isdigit())
    if len(digits) <= 4:
        return digits
    return digits[:3] + "*" * max(1, len(digits)-5) + digits[-2:]


async def show_profile(update_obj, context: ContextTypes.DEFAULT_TYPE):
    # can be called from CommandHandler or CallbackQuery
    if isinstance(update_obj, Update):
        update = update_obj
        user = update.message.from_user
        chat = update.message.chat
    else:
        # callback
        update = update_obj
        user = update.callback_query.from_user
        chat = update.callback_query.message.chat

    user_id = str(user.id)
    lang = users_data.get(user_id, {}).get("lang", "tg") or "tg"
    user = users_data.get(user_id, {})
    name = user.get("name") or "—"
    username = f"@{user.get('username')}" if user.get("username") else "—"
    phone = mask_phone(user.get("phone", "—"))
    # last game id from last order
    last_game = "—"
    last_product = "—"
    for o in reversed(orders):
        if str(o.get("user_id")) == user_id:
            last_game = o.get("game_id", "—")
            if o.get("type") == "free_uc":
                last_product = f"{o.get('pack',0)} UC (free)"
            else:
                last_product = f"{o.get('total',0)} TJS"
            break

    # cart summary
    cart = user_carts.get(user_id, {})
    cart_summary = "—"
    if cart:
        parts = []
        for pid, qty in cart.items():
            item = ITEMS.get(pid, {"name": f"#{pid}"})
            parts.append(f"{item['name']} x{qty}")
        cart_summary = ", ".join(parts)

    info_text = (
        f"👤 Ном: {name}\n"
        f"🔗 Username: {username}\n"
        f"📱 Рақам: {phone}\n"
        f"🎮 ID-бози: {last_game}\n"
        f"📦 Маҳсулот/Сабад: {cart_summary}\n"
        f"🔑 Код: {user.get('code', '—')}\n"
    )
    await chat.send_message(info_text)


# -------------------- Admin wrappers & small commands --------------------
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.message.from_user.id)
    lang = users_data.get(uid, {}).get("lang", "tg") or "tg"
    await update.message.reply_text({
        "tg": "🆘 Фармонҳо: /start, /help, /about, /language, /catalog, /cart, /wishlist, /profile",
        "ru": "🆘 Команды: /start, /help, /about, /language, /catalog, /cart, /wishlist, /profile",
        "en": "🆘 Commands: /start, /help, /about, /language, /catalog, /cart, /wishlist, /profile",
        "fa": "🆘 فرمان‌ها: /start, /help, /about, /language, /catalog, /cart, /wishlist, /profile"
    }[lang])


async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.message.from_user.id)
    lang = users_data.get(uid, {}).get("lang", "tg") or "tg"
    await update.message.reply_text(t("info_text", lang))


async def users_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if int(update.message.from_user.id) not in ADMIN_IDS:
        await update.message.reply_text("🚫 Only admin.")
        return
    if not users_data:
        await update.message.reply_text("No users.")
        return
    text = "Users:\n\n"
    for u in users_data.values():
        text += f"{u.get('name')} — {u.get('phone')} (id: {u.get('id')})\n"
    await update.message.reply_text(text)


# wrappers
async def catalog_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await catalog_handler(update, context)


async def cart_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # show cart (command)
    user_id = str(update.message.from_user.id)
    cart = user_carts.get(user_id, {})
    lang = users_data.get(user_id, {}).get("lang", "tg") or "tg"
    if not cart:
        await update.message.reply_text(t("cart_empty", lang))
        return
    # reuse show_cart_from_text logic
    await show_cart_from_text(update, context)


async def wishlist_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await open_wishlist_from_text(update, context)


async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.message.from_user.id)
    lang = users_data.get(uid, {}).get("lang", "tg") or "tg"
    await update.message.reply_text(t("info_text", lang))


async def profile_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await show_profile(update, context)


async def language_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # show inline language change buttons for existing users
    user = update.message.from_user
    user_id = str(user.id)
    buttons = []
    row = []
    for code, label in LANGUAGE_LABELS.items():
        row.append(InlineKeyboardButton(label, callback_data=f"setlang_change_{code}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    await update.message.reply_text(t("ask_language", users_data.get(user_id, {}).get("lang", "tg") or "tg"), reply_markup=InlineKeyboardMarkup(buttons))


# -------------------- Text handling --------------------
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = str(update.message.from_user.id)
    lang = users_data.get(user_id, {}).get("lang", "tg") or "tg"

    # broadcast mode
    if broadcast_mode.get(user_id):
        msg = text
        count = 0
        for uid in list(users_data.keys()):
            try:
                await context.bot.send_message(int(uid), f"📣 {msg}")
                count += 1
            except Exception:
                pass
        await update.message.reply_text(t("broadcast_sent", lang).format(count=count))
        broadcast_mode[user_id] = False
        return

    # priority inputs
    if context.user_data.get("awaiting_game_id"):
        await get_game_id(update, context)
        return
    if "awaiting_free_id" in context.user_data:
        await get_free_uc_id(update, context)
        return

    # if user hasn't provided phone yet -> trigger start flow
    if user_id not in users_data or not users_data[user_id].get("phone"):
        await start(update, context)
        return

    # Since menu now uses commands, most actions are handled by CommandHandlers.
    # Provide helpful fallback.
    await update.message.reply_text({"tg":"🤖 Лутфан аз тугмаҳои меню истифода баред.","ru":"🤖 Пожалуйста, используйте меню.","en":"🤖 Please use the menu buttons.","fa":"🤖 لطفاً از دکمه‌های منو استفاده کنید."}[lang])


# -------------------- Callback router --------------------
async def callback_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not query or not query.data:
        return
    data = query.data

    # Language callbacks
    if data.startswith("setlang_change_"):
        await set_language_callback(update, context)
        return

    # admin panel
    if data in ["admin_panel", "admin_users", "admin_orders", "admin_broadcast", "back_admin"]:
        await admin_panel_main(update, context)
        return

    # catalog/cart
    if data.startswith("select_"):
        await select_item_callback(update, context)
    elif data.startswith("addcart_"):
        await addcart_callback(update, context)
    elif data.startswith("addwish_"):
        await addwish_callback(update, context)
    elif data.startswith("removewish_"):
        await removewish_callback(update, context)
    elif data == "clear_cart":
        await clear_cart_callback(update, context)
    elif data == "checkout":
        await checkout_callback(update, context)
    elif data == "back_main":
        uid = str(query.from_user.id)
        await show_main_menu(query.message.chat, uid)
    # admin confirm/reject
    elif data.startswith("admin_confirm_"):
        await admin_confirm_callback(update, context)
    elif data.startswith("admin_reject_"):
        await admin_reject_callback(update, context)
    # legacy payment accept/reject
    elif data.startswith("payment_accept_") or data.startswith("payment_reject_"):
        await callback_payment_accept_reject(update, context)
    # payment methods
    elif data.startswith("pay_visa_") or data.startswith("pay_sber_"):
        await payment_method_callback(update, context)
    # admin verify proof
    elif data.startswith("pay_confirm_") or data.startswith("pay_reject_"):
        await admin_payment_verify(update, context)
    # free uc callbacks
    elif data == "check_sub_ucfree":
        await check_sub_callback(update, context)
    elif data == "daily_uc":
        await daily_uc_roll(update, context)
    elif data == "my_uc":
        await my_uc_info(update, context)
    elif data in ["claim_60", "claim_325"]:
        await claim_uc_button(update, context)
    elif data.startswith("admin_confirm_free_"):
        await admin_confirm_free(update, context)
    elif data.startswith("admin_reject_free_"):
        await admin_reject_free(update, context)
    elif data == "invite_link":
        await invite_link_callback(update, context)
    else:
        await query.answer()


# -------------------- Utility functions --------------------
async def admin_confirm_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    try:
        order_id = int(query.data.split("_")[-1])
    except Exception:
        return
    for o in orders:
        if o["id"] == order_id:
            if o["status"] != "pending":
                await query.message.reply_text(f"Order already in state: {o['status']}")
                return
            o["status"] = "awaiting_payment"
            save_all()
            try:
                await context.bot.send_message(int(o["user_id"]), f"Please pay to VISA: {VISA_NUMBER} and send proof.")
            except Exception:
                pass
            await query.message.reply_text("Payment info sent to user.")
            return
    await query.message.reply_text("Order not found.")


async def admin_reject_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    try:
        order_id = int(query.data.split("_")[-1])
    except Exception:
        return
    for o in orders:
        if o["id"] == order_id:
            if o["status"] != "pending":
                await query.message.reply_text(f"Order already in state: {o['status']}")
                return
            o["status"] = "rejected"
            save_all()
            try:
                await context.bot.send_message(int(o["user_id"]), "Your order was rejected. Contact admin.")
            except Exception:
                pass
            await query.message.reply_text("Order rejected.")
            return
    await query.message.reply_text("Order not found.")


async def invite_link_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    user = q.from_user
    uid = str(user.id)
    try:
        bot = await context.bot.get_me()
        bot_username = bot.username
    except Exception:
        await q.message.reply_text("⚠️ Bot username not found.")
        return
    invite_url = f"https://t.me/{bot_username}?start=invite_{uid}"
    lang = users_data.get(uid, {}).get("lang", "tg") or "tg"
    await q.message.reply_text(t("invite_text", lang).format(invite=invite_url))


def _create_order_record(user_id: str, total: int, extra=None) -> dict:
    order_id = random.randint(10000, 99999)
    order = {
        "id": order_id,
        "user_id": user_id,
        "user_name": users_data.get(user_id, {}).get("name", ""),
        "username": users_data.get(user_id, {}).get("username", ""),
        "phone": users_data.get(user_id, {}).get("phone", ""),
        "total": total,
        "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "pending",
        "extra": extra or {},
    }
    orders.append(order)
    save_all()
    return order


# -------------------- Main --------------------
def main():
    if TOKEN == "REPLACE_WITH_YOUR_BOT_TOKEN":
        print("Please set TOKEN in the script before running.")
        return

    app = ApplicationBuilder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("about", about_command))
    app.add_handler(CommandHandler("language", language_command))
    app.add_handler(CommandHandler("catalog", catalog_command))
    app.add_handler(CommandHandler("cart", cart_command))
    app.add_handler(CommandHandler("wishlist", wishlist_command))
    app.add_handler(CommandHandler("info", info_command))
    app.add_handler(CommandHandler("profile", profile_command))
    app.add_handler(CommandHandler("users", users_command))  # admin helper

    # CallbackQuery (single router)
    app.add_handler(CallbackQueryHandler(callback_router))

    # Contact handler (phone)
    app.add_handler(MessageHandler(filters.CONTACT, contact_handler))

    # Photos & Documents (payment proofs)
    app.add_handler(MessageHandler((filters.PHOTO | filters.Document.ALL) & (~filters.COMMAND), receive_payment_photo))

    # Text messages
    # Texts that are not commands are handled here (fallback)
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_text))

    print("✅ UCstore (Variant A) bot started!")
    app.run_polling()


if __name__ == "__main__":
    main()