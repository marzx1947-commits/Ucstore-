# Ucstore.py — Multilingual version (tj/en/ru/fa)
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

# -------------------- Config --------------------
TOKEN = "8524676045:AAHXHO6tYovrMAAGxAQZUi2Z-TGFBUPeMyY"  # <-- change this
ADMIN_IDS = [8436218638]
USERS_FILE = "users.json"
ORDERS_FILE = "orders.json"

ITEMS = {
    1: {"name": "60 UC", "price": 10},
    2: {"name": "325 UC", "price": 50},
    3: {"name": "660 UC", "price": 100},
    4: {"name": "1800 UC", "price": 250},
    5: {"name": "3850 UC", "price": 500},
    6: {"name": "8100 UC", "price": 1000},
}

ADMIN_INFO_TJ = (
    "UCstore — ин боти расмии фурӯши UC барои PUBG Mobile ва дигар хидматҳои рақамии бозӣ мебошад. "
    "Бо UCstore шумо ҳамеша бехатар, зуд ва бо эътимод харид мекунед 💪"
)

VISA_NUMBER = "4439200020432471"
SBER_NUMBER = "2202208496090011"
FREE_UC_CHANNEL = "@marzbon_media"

# -------------------- Multilanguage texts --------------------
# Keys used through the code. Add translations here.
LANG = {
    "tj": {
        "ask_contact": "🔐 Барои истифодаи бот рақами телефони худро фиристед:",
        "already_registered": "👋 Салом, {name}!",
        "contact_missing": "⚠️ Лутфан контакт фиристед.",
        "registered_ok": "✅ Шумо бо муваффақият ворид шудед!!\n🔑 Код шумо: {code}",
        "notify_admin_new_user": "👤 Корбари нав сабт шуд!\n\n🧑 Ном: {name}\n📱 Рақам: {phone}\n🔗 @{username}\n🔑 Код: {code}",
        "main_menu_text": "Менюи асосӣ:",
        "catalog": "🛍 Каталог",
        "wishlist": "❤️ Дилхоҳҳо",
        "cart": "🛒 Сабад",
        "admin_profile": "💬 Профили админ",
        "info": "ℹ Маълумот",
        "free_uc": "🎁 UC ройгон",
        "admin_panel": "👑 Панели админ",
        "catalog_title": "🛍 Каталог:",
        "product_added_cart": "✅ {name} ба сабад илова шуд!",
        "product_added_wish": "❤️ {name} ба дилхоҳҳо илова шуд!",
        "wishlist_empty": "❤️ Дилхоҳҳо холист.",
        "cart_empty": "🛒 Сабад холист.",
        "cart_contents_header": "🛍 Маҳсулоти шумо:\n",
        "checkout_ask_game_id": "🎮 Лутфан ID-и бозии худро ворид кунед (фақат рақамҳо):",
        "only_digits": "⚠️ Лутфан танҳо рақам ворид кунед (ID-и бозӣ бояд рақам бошад).",
        "choose_payment": "Лутфан тарзи пардохтро интихоб кунед:",
        "payment_card_info": "💳 Тарзи пардохт: {method}\n📌 Рақами корт/ҳисоб: {card}\n\nПас аз пардохт, лутфан квитанцияро ҳамчун акс ё файл ба ин чат фиристед.",
        "no_pending_order_for_proof": "⚠️ Шумо ҳоло фармоиши интизори квитанция надоред.",
        "photo_or_doc": "⚠️ Лутфан акс ё файл равон кунед!",
        "proof_received": "✅ Квитанция қабул шуд! Мунтазир шавед, то админ тасдиқ кунад.",
        "payment_confirmed_user": "✅ Пардохти шумо барои фармоиши №{order_id} тасдиқ шуд! Ташаккур.",
        "payment_rejected_user": "❌ Пардохти шумо барои фармоиши №{order_id} рад шуд. Лутфан бо админ тамос гиред.",
        "free_uc_menu_title": "🎁 Менюи UC ройгон:",
        "not_registered_start": "⚠️ Аввал /start кунед.",
        "subscribe_channel": "📢 Обуна шудан",
        "check_subscription": "🔄 Санҷиш",
        "get_daily_uc": "🎲 Гирифтани UC-и рӯзона",
        "my_uc": "📊 UC-и ҷамъшуда",
        "claim_60": "🎁 60 UC",
        "claim_325": "🎁 325 UC",
        "invite_friends": "🔗 Даъвати дӯстон",
        "daily_already_got": "⏳ Шумо аллакай UC гирифтед. Ба шумо боз {hours} соат мондааст.",
        "daily_roll_result": "🎉 Шумо {roll} UC гирифтед!\n📊 Ҳамагӣ: {total} UC",
        "my_uc_info": "📊 Шумо доред: {amount} UC",
        "not_enough_uc": "❌ Шумо UC кофӣ надоред. Шумо доред: {have} UC",
        "enter_pubg_id_free": "🎮 Лутфан ID-и PUBG-ро ворид кунед (8–15 рақам):",
        "free_request_sent": "🎁 Дархости {amount} UC ба админ фиристода шуд! (Фармоиш №{order_id})",
        "admin_confirmed": "✅ Тасдиқ шуд.",
        "admin_rejected": "❌ Рад шуд.",
        "broadcast_prompt": "✏️ Ҳозир матни паёмро навис — ман онро ба *ҳама корбарҳо* мефиристам.",
        "broadcast_sent": "✅ Паём ба {count} корбар фиристода шуд.",
        "use_menu_buttons": "🤖 Лутфан аз тугмаҳои меню истифода баред.",
        "language_choose_title": "🔤 Лутфан забонро интихоб кунед:",
        "language_changed": "✅ Забон ба {lang_name} иваз шуд.",
        "language_current": "Ҳозир забон: {lang_name}",
        "language_command_info": "Иваз кардани забон: /language",
        "ask_game_id_after_checkout": "🎮 Лутфан ID-и бозии худро ворид кунед (фақат рақамҳо):",
        "invalid_order": "⚠️ Фармоиш ёфт нашуд.",
        "please_set_token": "Please set TOKEN in the script before running.",
        "bot_started": "✅ UCstore бот фаъол шуд!",
    },
    "en": {
        "ask_contact": "🔐 Please send your phone number to use the bot:",
        "already_registered": "👋 Hello, {name}!",
        "contact_missing": "⚠️ Please send a contact.",
        "registered_ok": "✅ You have successfully registered!!\n🔑 Your code: {code}",
        "notify_admin_new_user": "👤 New user registered!\n\n🧑 Name: {name}\n📱 Phone: {phone}\n🔗 @{username}\n🔑 Code: {code}",
        "main_menu_text": "Main menu:",
        "catalog": "🛍 Shop",
        "wishlist": "❤️ Favorites",
        "cart": "🛒 Cart",
        "admin_profile": "💬 Admin Support",
        "info": "ℹ Information",
        "free_uc": "🎁 Free UC",
        "admin_panel": "👑 Admin panel",
        "catalog_title": "🛍 Catalog:",
        "product_added_cart": "✅ {name} added to cart!",
        "product_added_wish": "❤️ {name} added to wishlist!",
        "wishlist_empty": "❤️ Wishlist is empty.",
        "cart_empty": "🛒 Cart is empty.",
        "cart_contents_header": "🛍 Your items:\n",
        "checkout_ask_game_id": "🎮 Please enter your game ID (digits only):",
        "only_digits": "⚠️ Please enter digits only (game ID must be numeric).",
        "choose_payment": "Please choose a payment method:",
        "payment_card_info": "💳 Payment method: {method}\n📌 Card/account number: {card}\n\nAfter payment, please send the receipt as a photo or file to this chat.",
        "no_pending_order_for_proof": "⚠️ You don't have an order awaiting receipt.",
        "photo_or_doc": "⚠️ Please send a photo or file!",
        "proof_received": "✅ Receipt received! Wait for admin confirmation.",
        "payment_confirmed_user": "✅ Your payment for order #{order_id} has been confirmed! Thank you.",
        "payment_rejected_user": "❌ Your payment for order #{order_id} was rejected. Please contact admin.",
        "free_uc_menu_title": "🎁 Free UC menu:",
        "not_registered_start": "⚠️ First use /start.",
        "subscribe_channel": "📢 Subscribe",
        "check_subscription": "🔄 Check",
        "get_daily_uc": "🎲 Get daily UC",
        "my_uc": "📊 My UC",
        "claim_60": "🎁 60 UC",
        "claim_325": "🎁 325 UC",
        "invite_friends": "🔗 Invite friends",
        "daily_already_got": "⏳ You already got UC today. {hours} hours left.",
        "daily_roll_result": "🎉 You got {roll} UC!\n📊 Total: {total} UC",
        "my_uc_info": "📊 You have: {amount} UC",
        "not_enough_uc": "❌ Not enough UC. You have: {have} UC",
        "enter_pubg_id_free": "🎮 Please enter PUBG ID (8–15 digits):",
        "free_request_sent": "🎁 Request for {amount} UC sent to admin! (Order #{order_id})",
        "admin_confirmed": "✅ Confirmed.",
        "admin_rejected": "❌ Rejected.",
        "broadcast_prompt": "✏️ Send the message now — I will forward it to *all users*.",
        "broadcast_sent": "✅ Message sent to {count} users.",
        "use_menu_buttons": "🤖 Please use the menu buttons.",
        "language_choose_title": "🔤 Please choose a language:",
        "language_changed": "✅ Language changed to {lang_name}.",
        "language_current": "Current language: {lang_name}",
        "language_command_info": "Change language: /language",
        "ask_game_id_after_checkout": "🎮 Please enter your game ID (digits only):",
        "invalid_order": "⚠️ Order not found.",
        "please_set_token": "Please set TOKEN in the script before running.",
        "bot_started": "✅ UCstore bot started!",
    },
    "ru": {
        "ask_contact": "🔐 Для использования бота отправьте, пожалуйста, ваш номер телефона:",
        "already_registered": "👋 Привет, {name}!",
        "contact_missing": "⚠️ Пожалуйста, отправьте контакт.",
        "registered_ok": "✅ Вы успешно зарегистрированы!!\n🔑 Ваш код: {code}",
        "notify_admin_new_user": "👤 Новый пользователь зарегистрировался!\n\n🧑 Имя: {name}\n📱 Телефон: {phone}\n🔗 @{username}\n🔑 Код: {code}",
        "main_menu_text": "Главное меню:",
        "catalog": "🛍 Каталог",
        "wishlist": "❤️ Избранное",
        "cart": "🛒 Корзина",
        "admin_profile": "💬 Связь с админом",
        "info": "ℹ Информация",
        "free_uc": "🎁 Бесплатные UC",
        "admin_panel": "👑 Панель админа",
        "catalog_title": "🛍 Каталог:",
        "product_added_cart": "✅ {name} добавлен в корзину!",
        "product_added_wish": "❤️ {name} добавлен в желания!",
        "wishlist_empty": "❤️ Список желаний пуст.",
        "cart_empty": "🛒 Корзина пуста.",
        "cart_contents_header": "🛍 Ваши товары:\n",
        "checkout_ask_game_id": "🎮 Пожалуйста, введите ваш игровой ID (только цифры):",
        "only_digits": "⚠️ Пожалуйста, вводите только цифры (ID должен быть числовым).",
        "choose_payment": "Пожалуйста, выберите способ оплаты:",
        "payment_card_info": "💳 Способ оплаты: {method}\n📌 Номер карты/счета: {card}\n\nПосле оплаты, пожалуйста, отправьте чек как фото или файл в этот чат.",
        "no_pending_order_for_proof": "⚠️ У вас нет заказов, ожидающих квитанции.",
        "photo_or_doc": "⚠️ Пожалуйста, отправьте фото или файл!",
        "proof_received": "✅ Квитанция получена! Ожидайте подтверждения админа.",
        "payment_confirmed_user": "✅ Ваша оплата за заказ #{order_id} подтверждена! Спасибо.",
        "payment_rejected_user": "❌ Ваша оплата за заказ #{order_id} отклонена. Пожалуйста, свяжитесь с админом.",
        "free_uc_menu_title": "🎁 Меню бесплатных UC:",
        "not_registered_start": "⚠️ Сначала используйте /start.",
        "subscribe_channel": "📢 Подписаться",
        "check_subscription": "🔄 Проверить",
        "get_daily_uc": "🎲 Получить ежедневные UC",
        "my_uc": "📊 Мои UC",
        "claim_60": "🎁 60 UC",
        "claim_325": "🎁 325 UC",
        "invite_friends": "🔗 Пригласить друзей",
        "daily_already_got": "⏳ Вы уже получили UC сегодня. Осталось {hours} часов.",
        "daily_roll_result": "🎉 Вы получили {roll} UC!\n📊 Всего: {total} UC",
        "my_uc_info": "📊 У вас: {amount} UC",
        "not_enough_uc": "❌ Недостаточно UC. У вас: {have} UC",
        "enter_pubg_id_free": "🎮 Пожалуйста, введите PUBG ID (8–15 цифр):",
        "free_request_sent": "🎁 Запрос на {amount} UC отправлен администратору! (Заказ #{order_id})",
        "admin_confirmed": "✅ Подтверждено.",
        "admin_rejected": "❌ Отклонено.",
        "broadcast_prompt": "✏️ Сейчас напишите сообщение — я перешлю его всем пользователям.",
        "broadcast_sent": "✅ Сообщение отправлено {count} пользователям.",
        "use_menu_buttons": "🤖 Пожалуйста, используйте кнопки меню.",
        "language_choose_title": "🔤 Пожалуйста, выберите язык:",
        "language_changed": "✅ Язык изменён на {lang_name}.",
        "language_current": "Текущий язык: {lang_name}",
        "language_command_info": "Сменить язык: /language",
        "ask_game_id_after_checkout": "🎮 Пожалуйста, введите ваш игровой ID (только цифры):",
        "invalid_order": "⚠️ Заказ не найден.",
        "please_set_token": "Please set TOKEN in the script before running.",
        "bot_started": "✅ UCstore бот запущен!",
    },
    "fa": {
        "ask_contact": "🔐 لطفاً برای استفاده از ربات شماره تلفن خود را ارسال کنید:",
        "already_registered": "👋 سلام، {name}!",
        "contact_missing": "⚠️ لطفاً مخاطب ارسال کنید.",
        "registered_ok": "✅ با موفقیت ثبت شدید!!\n🔑 کد شما: {code}",
        "notify_admin_new_user": "👤 کاربر جدید ثبت شد!\n\n🧑 نام: {name}\n📱 تلفن: {phone}\n🔗 @{username}\n🔑 کد: {code}",
        "main_menu_text": "منوی اصلی:",
        "catalog": "🛍 فروشگاه",
        "wishlist": "❤️ مورد علاقه‌ها",
        "cart": "🛒 سبد خرید",
        "admin_profile": "💬 پشتیبانی ادمین",
        "info": "ℹ اطلاعات",
        "free_uc": "🎁 UC رایگان",
        "admin_panel": "👑 پنل ادمین",
        "catalog_title": "🛍 کاتالوگ:",
        "product_added_cart": "✅ {name} به سبد اضافه شد!",
        "product_added_wish": "❤️ {name} به علاقه‌مندی‌ها اضافه شد!",
        "wishlist_empty": "❤️ لیست علاقه‌مندی‌ها خالی است.",
        "cart_empty": "🛒 سبد خرید خالی است.",
        "cart_contents_header": "🛍 اقلام شما:\n",
        "checkout_ask_game_id": "🎮 لطفاً شناسه بازی خود را وارد کنید (فقط ارقام):",
        "only_digits": "⚠️ لطفاً فقط ارقام وارد کنید (شناسه بازی باید عددی باشد).",
        "choose_payment": "لطفاً روش پرداخت را انتخاب کنید:",
        "payment_card_info": "💳 روش پرداخت: {method}\n📌 شماره کارت/حساب: {card}\n\nبعد از پرداخت، لطفاً رسید را به صورت عکس یا فایل در این چت ارسال کنید.",
        "no_pending_order_for_proof": "⚠️ در حال حاضر سفارشی برای ارائه رسید ندارید.",
        "photo_or_doc": "⚠️ لطفاً عکس یا فایل ارسال کنید!",
        "proof_received": "✅ رسید دریافت شد! منتظر تایید ادمین باشید.",
        "payment_confirmed_user": "✅ پرداخت شما برای سفارش #{order_id} تایید شد! متشکریم.",
        "payment_rejected_user": "❌ پرداخت شما برای سفارش #{order_id} رد شد. لطفاً با ادمین تماس بگیرید.",
        "free_uc_menu_title": "🎁 منوی UC رایگان:",
        "not_registered_start": "⚠️ ابتدا /start را بزنید.",
        "subscribe_channel": "📢 عضویت",
        "check_subscription": "🔄 بررسی",
        "get_daily_uc": "🎲 دریافت UC روزانه",
        "my_uc": "📊 UC من",
        "claim_60": "🎁 60 UC",
        "claim_325": "🎁 325 UC",
        "invite_friends": "🔗 دعوت از دوستان",
        "daily_already_got": "⏳ شما امروز قبلاً UC دریافت کرده‌اید. {hours} ساعت مانده.",
        "daily_roll_result": "🎉 شما {roll} UC دریافت کردید!\n📊 جمع: {total} UC",
        "my_uc_info": "📊 شما دارید: {amount} UC",
        "not_enough_uc": "❌ UC کافی ندارید. شما دارید: {have} UC",
        "enter_pubg_id_free": "🎮 لطفاً شناسه PUBG را وارد کنید (8–15 رقم):",
        "free_request_sent": "🎁 درخواست {amount} UC به ادمین ارسال شد! (سفارش #{order_id})",
        "admin_confirmed": "✅ تایید شد.",
        "admin_rejected": "❌ رد شد.",
        "broadcast_prompt": "✏️ حالا متن پیام را بنویسید — من آن را برای همه کاربران ارسال می‌کنم.",
        "broadcast_sent": "✅ پیام به {count} کاربر ارسال شد.",
        "use_menu_buttons": "🤖 لطفاً از دکمه‌های منو استفاده کنید.",
        "language_choose_title": "🔤 لطفاً زبان را انتخاب کنید:",
        "language_changed": "✅ زبان به {lang_name} تغییر یافت.",
        "language_current": "زبان فعلی: {lang_name}",
        "language_command_info": "تغییر زبان: /language",
        "ask_game_id_after_checkout": "🎮 لطفاً شناسه بازی خود را وارد کنید (فقط ارقام):",
        "invalid_order": "⚠️ سفارش یافت نشد.",
        "please_set_token": "Please set TOKEN in the script before running.",
        "bot_started": "✅ ربات UCstore فعال شد!",
    },
}

# Map code -> display name
LANG_NAMES = {
    "tj": "Тоҷикӣ",
    "en": "English",
    "ru": "Русский",
    "fa": "فارسی",
}

DEFAULT_LANG = "tj"  # primary language

# -------------------- Persistence --------------------

def load_json(path, default):
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return default
    return default


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def save_all():
    save_json(USERS_FILE, users_data)
    save_json(ORDERS_FILE, orders)


users_data = load_json(USERS_FILE, {})  # key: user_id (str) -> info
orders = load_json(ORDERS_FILE, [])  # list of orders

# Runtime structures (not persisted)
user_carts = {}
user_wishlist = {}
broadcast_mode = {}

# -------------------- Language helpers --------------------

def get_user_lang(user_id: str):
    u = users_data.get(str(user_id))
    if not u:
        return DEFAULT_LANG
    settings = u.get("settings", {})
    return settings.get("language", DEFAULT_LANG)

def set_user_language(user_id: str, lang_code: str):
    uid = str(user_id)
    if uid not in users_data:
        users_data[uid] = {"id": int(uid), "settings": {"language": lang_code}}
    else:
        users_data[uid].setdefault("settings", {})["language"] = lang_code
    save_all()

def get_text_for_lang(lang_code: str, key: str, **kwargs):
    # fallback chain: requested lang -> default lang -> en -> first available
    if lang_code in LANG and key in LANG[lang_code]:
        return LANG[lang_code][key].format(**kwargs)
    if DEFAULT_LANG in LANG and key in LANG[DEFAULT_LANG]:
        return LANG[DEFAULT_LANG][key].format(**kwargs)
    # fallback to any language that has key
    for l in LANG:
        if key in LANG[l]:
            return LANG[l][key].format(**kwargs)
    return key

def get_text(user_id_or_obj, key: str, **kwargs):
    # Accept either numeric user id or telegram user object
    if hasattr(user_id_or_obj, "id"):
        uid = str(user_id_or_obj.id)
    else:
        uid = str(user_id_or_obj)
    lang = get_user_lang(uid)
    return get_text_for_lang(lang, key, **kwargs)

# -------------------- Helpers --------------------

def generate_user_code(length: int = 6) -> str:
    chars = string.ascii_uppercase + string.digits
    return "".join(random.choice(chars) for _ in range(length))


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


# -------------------- Handlers --------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Entry point. Ask for phone contact if user not registered.
    if not update.message:
        return

    user = update.message.from_user
    user_id = str(user.id)

    # If already registered, show menu
    if user_id in users_data:
        await update.message.reply_text(get_text(user_id, "already_registered", name=user.first_name or ""))
        await show_main_menu(update.message.chat, user_id)
        return

    # Ask for contact (button label kept simple)
    contact_button = KeyboardButton("📱 " + get_text(DEFAULT_LANG, "ask_contact"), request_contact=True)
    reply_markup = ReplyKeyboardMarkup([[contact_button]], resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text(get_text(DEFAULT_LANG, "ask_contact"), reply_markup=reply_markup)

async def get_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Save contact and create user record
    contact = update.message.contact
    if not contact:
        await update.message.reply_text(get_text(DEFAULT_LANG, "contact_missing"))
        return

    user = update.message.from_user
    user_id = str(user.id)

    user_code = generate_user_code(6)
    users_data[user_id] = {
        "id": user.id,
        "name": user.first_name or "",
        "username": user.username or "",
        "phone": contact.phone_number,
        "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "free_uc": 0,
        "last_claim": None,
        "last_daily_uc": None,
        "code": user_code,
        # settings block as requested (variant 3)
        "settings": {"language": DEFAULT_LANG},
    }
    save_all()

    # After registration — ask to choose language (show inline buttons)
    buttons = []
    for code, name in LANG_NAMES.items():
        buttons.append(InlineKeyboardButton(f"{name}", callback_data=f"setlang_{code}"))
    # put in rows of 2
    rows = [buttons[i:i+2] for i in range(0, len(buttons), 2)]
    rows.append([InlineKeyboardButton(get_text(DEFAULT_LANG, "language_command_info"), callback_data="language_info")])
    await update.message.reply_text(get_text(DEFAULT_LANG, "registered_ok", code=user_code), reply_markup=ReplyKeyboardRemove())
    await update.message.reply_text(get_text(DEFAULT_LANG, "language_choose_title"), reply_markup=InlineKeyboardMarkup(rows))

    # Handle inviter stored in user_data (if /start payload was used)
    inviter = context.user_data.get("invited_by")
    if inviter and inviter != user_id and str(inviter) in users_data:
        inv = str(inviter)
        users_data[inv]["free_uc"] = users_data[inv].get("free_uc", 0) + 2
        save_all()
        try:
            await context.bot.send_message(
                int(inv),
                get_text(inv, "notify_admin_new_user", name=user.first_name or "", phone=contact.phone_number, username=user.username or "-", code=user_code)
            )
        except Exception:
            pass

    # Notify admins (in default language for consistency, include user preferred later)
    for admin in ADMIN_IDS:
        try:
            await context.bot.send_message(
                admin,
                get_text(DEFAULT_LANG, "notify_admin_new_user", name=user.first_name or "", phone=contact.phone_number, username=user.username or "-", code=user_code)
            )
        except Exception:
            pass

async def show_main_menu(chat, user_id: str):
    # build menu labels according to user's language
    uid = str(user_id)
    btns = [
        [get_text(uid, "catalog"), get_text(uid, "wishlist")],
        [get_text(uid, "cart"), get_text(uid, "admin_profile")],
        [get_text(uid, "info"), get_text(uid, "free_uc")],
    ]
    if int(user_id) in ADMIN_IDS:
        btns.append([get_text(uid, "admin_panel")])
    reply_markup = ReplyKeyboardMarkup(btns, resize_keyboard=True, one_time_keyboard=False)
    await chat.send_message(get_text(uid, "main_menu_text"), reply_markup=reply_markup)

# Catalog handlers
async def catalog_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target = update.message or (update.callback_query and update.callback_query.message)
    if not target:
        return

    uid = str((update.message.from_user if update.message else update.callback_query.from_user).id)
    buttons = []
    row = []
    for i, item in ITEMS.items():
        row.append(InlineKeyboardButton(f"{item['name']} — {item['price']} TJS", callback_data=f"select_{i}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([InlineKeyboardButton("⬅️ " + get_text(uid, "main_menu_text"), callback_data="back_main")])

    await target.reply_text(get_text(uid, "catalog_title"), reply_markup=InlineKeyboardMarkup(buttons))


async def select_item_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    try:
        item_id = int(query.data.split("_")[1])
    except Exception:
        await query.message.reply_text("⚠️")
        return

    item = ITEMS.get(item_id)
    if not item:
        await query.message.reply_text(get_text(get_user_lang(query.from_user.id), "invalid_order"))
        return

    uid = str(query.from_user.id)
    buttons = [
        [InlineKeyboardButton("🛒 " + get_text(uid, "cart"), callback_data=f"addcart_{item_id}"),
         InlineKeyboardButton("❤️ " + get_text(uid, "wishlist"), callback_data=f"addwish_{item_id}")],
        [InlineKeyboardButton("⬅️ " + get_text(uid, "main_menu_text"), callback_data="back_main")],
    ]
    await query.message.reply_text(f"{item['name']} — {item['price']} TJS", reply_markup=InlineKeyboardMarkup(buttons))


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
    await query.message.reply_text(get_text(user_id, "product_added_cart", name=ITEMS[item_id]["name"]))


async def addwish_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)
    try:
        item_id = int(query.data.split("_")[1])
    except Exception:
        return
    user_wishlist.setdefault(user_id, set()).add(item_id)
    await query.message.reply_text(get_text(user_id, "product_added_wish", name=ITEMS[item_id]["name"]))


async def open_wishlist_from_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    wishlist = user_wishlist.get(user_id, set())
    if not wishlist:
        await update.message.reply_text(get_text(user_id, "wishlist_empty"))
        return

    for i in list(wishlist):
        item = ITEMS.get(i)
        if not item:
            continue
        buttons = [
            [InlineKeyboardButton("🛒 " + get_text(user_id, "cart"), callback_data=f"addcart_{i}"),
             InlineKeyboardButton("🗑️ Хок кардан", callback_data=f"removewish_{i}")]
        ]
        await update.message.reply_text(f"{item['name']} — {item['price']} TJS", reply_markup=InlineKeyboardMarkup(buttons))


async def removewish_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer(get_text(get_user_lang(query.from_user.id), "admin_rejected"))
    user_id = str(query.from_user.id)
    try:
        item_id = int(query.data.split("_")[1])
    except Exception:
        return
    if user_id in user_wishlist:
        user_wishlist[user_id].discard(item_id)
    try:
        await query.message.delete()
    except Exception:
        pass

# Cart and checkout
async def show_cart_from_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    cart = user_carts.get(user_id, {})
    if not cart:
        await update.message.reply_text(get_text(user_id, "cart_empty"))
        return

    text = get_text(user_id, "cart_contents_header")
    total = 0
    for i, qty in cart.items():
        item = ITEMS.get(i)
        if not item:
            continue
        subtotal = item["price"] * qty
        total += subtotal
        text += f"- {item['name']} x{qty} = {subtotal} TJS\n"
    text += f"💰 Ҳамагӣ: {total} TJS"

    buttons = [
        [InlineKeyboardButton("📦 " + get_text(user_id, "checkout_ask_game_id"), callback_data="checkout"),
         InlineKeyboardButton("🗑️ Пок кардан", callback_data="clear_cart")],
        [InlineKeyboardButton("⬅️ " + get_text(user_id, "main_menu_text"), callback_data="back_main")],
    ]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons))

async def clear_cart_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("🧹")
    user_id = str(query.from_user.id)
    user_carts[user_id] = {}

async def checkout_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)
    cart = user_carts.get(user_id, {})
    if not cart:
        await query.message.reply_text(get_text(user_id, "cart_empty"))
        return

    await query.message.reply_text(get_text(user_id, "checkout_ask_game_id"))
    context.user_data["awaiting_game_id"] = True
    context.user_data["pending_order_total"] = sum(ITEMS[i]["price"] * q for i, q in cart.items())

async def get_game_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("awaiting_game_id"):
        return
    game_id = update.message.text.strip()
    if not game_id.isdigit():
        await update.message.reply_text(get_text(update.message.from_user.id, "only_digits"))
        return

    context.user_data["awaiting_game_id"] = False

    user_id = str(update.message.from_user.id)
    total = context.user_data.pop("pending_order_total", 0)

    # Create order and ask for payment method
    order = _create_order_record(user_id, total)
    order["game_id"] = game_id
    order["status"] = "choose_payment"
    save_all()

    # Two payment buttons
    buttons = [
        [InlineKeyboardButton("💳 VISA", callback_data=f"pay_visa_{order['id']}")],
        [InlineKeyboardButton("🏦 SberBank", callback_data=f"pay_sber_{order['id']}")]
    ]

    await update.message.reply_text(
        f"Фармоиш №{order['id']} \n"
        f"🎮 ID: {game_id}\n"
        f"💰 Нархи умумӣ: {total} TJS\n\n"
        + get_text(user_id, "choose_payment"),
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# New: payment method selection handler
async def payment_method_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    parts = data.split("_")
    if len(parts) < 3:
        await query.message.reply_text("⚠️")
        return

    method = parts[1]          # visa / sber
    try:
        order_id = int(parts[2])
    except Exception:
        await query.message.reply_text("⚠️")
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

            await query.message.reply_text(get_text(get_user_lang(query.from_user.id), "payment_card_info", method=method_name, card=card))
            return

    await query.message.reply_text(get_text(get_user_lang(query.from_user.id), "invalid_order"))

# Payment proof receive (photo or document)
async def receive_payment_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)

    # Find last order from this user that is awaiting proof
    order = None
    for o in reversed(orders):
        if str(o.get("user_id")) == user_id and o.get("status") == "awaiting_proof":
            order = o
            break

    if not order:
        await update.message.reply_text(get_text(user_id, "no_pending_order_for_proof"))
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
        await update.message.reply_text(get_text(user_id, "photo_or_doc"))
        return

    order["status"] = "proof_sent"
    order["proof_file"] = file_id
    save_all()

    caption = (
        f"📦 Фармоиши №{order['id']}\n"
        f"👤 @{order.get('username') or order.get('user_name')}\n"
        f"🎮 ID: {order.get('game_id')}\n"
        f"💰 {order.get('total')} TJS\n"
        f"💳 Тарзи пардохт: {order.get('payment_method')}\n"
        f"📱 Рақами корбар: {order.get('phone') or '—'}\n"
        f"🕒 {order.get('time')}"
    )

    buttons = [
        [
            InlineKeyboardButton("✅ Тасдиқ", callback_data=f"pay_confirm_{order['id']}"),
            InlineKeyboardButton("❌ Рад", callback_data=f"pay_reject_{order['id']}")
        ]
    ]

    for admin in ADMIN_IDS:
        try:
            if is_photo:
                await context.bot.send_photo(
                    chat_id=admin,
                    photo=file_id,
                    caption=caption,
                    reply_markup=InlineKeyboardMarkup(buttons),
                )
            else:
                await context.bot.send_document(
                    chat_id=admin,
                    document=file_id,
                    caption=caption,
                    reply_markup=InlineKeyboardMarkup(buttons),
                )
        except Exception:
            pass

    await update.message.reply_text(get_text(user_id, "proof_received"))

# Admin confirm/reject for payments (pay_confirm_, pay_reject_)
async def admin_payment_verify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    parts = query.data.split("_")
    if len(parts) < 3:
        await query.message.reply_text("⚠️")
        return

    action = parts[1]       # confirm / reject
    try:
        order_id = int(parts[2])
    except Exception:
        await query.message.reply_text("⚠️")
        return

    for order in orders:
        if order["id"] == order_id:
            user_chat = int(order["user_id"])
            if action == "confirm":
                order["status"] = "confirmed"
                save_all()
                try:
                    await context.bot.send_message(user_chat, get_text(user_chat, "payment_confirmed_user", order_id=order_id))
                except Exception:
                    pass
                await query.message.reply_text(get_text(get_user_lang(query.from_user.id), "admin_confirmed"))
            else:
                order["status"] = "rejected"
                save_all()
                try:
                    await context.bot.send_message(user_chat, get_text(user_chat, "payment_rejected_user", order_id=order_id))
                except Exception:
                    pass
                await query.message.reply_text(get_text(get_user_lang(query.from_user.id), "admin_rejected"))
            return

    await query.message.reply_text(get_text(get_user_lang(query.from_user.id), "invalid_order"))

# Existing callback handlers for other flows remain (payment_accept/reject for another flow)
async def callback_payment_accept_reject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("payment_accept_"):
        parts = data.split("_")
        try:
            order_id = int(parts[2])
            user_id = int(parts[3])
        except Exception:
            await query.message.reply_text("⚠️")
            return
        for o in orders:
            if o["id"] == order_id and str(o["user_id"]) == str(user_id):
                o["status"] = "confirmed"
                save_all()
                try:
                    await context.bot.send_message(int(user_id), get_text(user_id, "payment_confirmed_user", order_id=order_id))
                except Exception:
                    pass
                await query.message.reply_text(get_text(get_user_lang(query.from_user.id), "admin_confirmed"))
                return
        await query.message.reply_text(get_text(get_user_lang(query.from_user.id), "invalid_order"))

    elif data.startswith("payment_reject_"):
        parts = data.split("_")
        try:
            order_id = int(parts[2])
            user_id = int(parts[3])
        except Exception:
            await query.message.reply_text("⚠️")
            return
        for o in orders:
            if o["id"] == order_id and str(o["user_id"]) == str(user_id):
                o["status"] = "rejected"
                save_all()
                try:
                    await context.bot.send_message(int(user_id), get_text(user_id, "payment_rejected_user", order_id=order_id))
                except Exception:
                    pass
                await query.message.reply_text(get_text(get_user_lang(query.from_user.id), "admin_rejected"))
                return
        await query.message.reply_text(get_text(get_user_lang(query.from_user.id), "invalid_order"))

# Free UC system
async def free_uc_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.message.chat if update.message else update.callback_query.message.chat
    from_user = update.message.from_user if update.message else update.callback_query.from_user
    user_id = str(from_user.id)

    if user_id not in users_data:
        await chat.send_message(get_text(user_id, "not_registered_start"))
        return

    subscribed = False
    try:
        member = await context.bot.get_chat_member(FREE_UC_CHANNEL, int(user_id))
        subscribed = member.status in ["member", "administrator", "creator"]
    except Exception:
        subscribed = False

    buttons = []
    if subscribed:
        buttons.append([InlineKeyboardButton(get_text(user_id, "get_daily_uc"), callback_data="daily_uc")])
        buttons.append([InlineKeyboardButton(get_text(user_id, "my_uc"), callback_data="my_uc")])
        buttons.append([
            InlineKeyboardButton(get_text(user_id, "claim_60"), callback_data="claim_60"),
            InlineKeyboardButton(get_text(user_id, "claim_325"), callback_data="claim_325"),
        ])
    else:
        channel_url = f"https://t.me/{FREE_UC_CHANNEL.lstrip('@')}"
        buttons.append([InlineKeyboardButton(get_text(user_id, "subscribe_channel"), url=channel_url)])
        buttons.append([InlineKeyboardButton(get_text(user_id, "check_subscription"), callback_data="check_sub_ucfree")])

    buttons.append([InlineKeyboardButton(get_text(user_id, "invite_friends"), callback_data="invite_link")])
    await chat.send_message(get_text(user_id, "free_uc_menu_title"), reply_markup=InlineKeyboardMarkup(buttons))

async def check_sub_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    await free_uc_menu(update, context)

async def daily_uc_roll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    user_id = str(q.from_user.id)
    user = users_data.get(user_id)
    if not user:
        await q.message.reply_text(get_text(user_id, "not_registered_start"))
        return

    now = datetime.datetime.now()
    last = user.get("last_daily_uc")
    if last:
        try:
            last_dt = datetime.datetime.strptime(last, "%Y-%m-%d %H:%M:%S")
            if (now - last_dt).total_seconds() < 24 * 3600:
                remaining = int((24 * 3600 - (now - last_dt).total_seconds()) // 3600)
                await q.message.reply_text(get_text(user_id, "daily_already_got", hours=remaining))
                return
        except Exception:
            pass

    roll = random.choices([1, 2, 3, 4, 5], weights=[70, 20, 7, 2, 1])[0]
    user["free_uc"] = user.get("free_uc", 0) + roll
    user["last_daily_uc"] = now.strftime("%Y-%m-%d %H:%M:%S")
    users_data[user_id] = user
    save_all()
    await q.message.reply_text(get_text(user_id, "daily_roll_result", roll=roll, total=user["free_uc"]))

async def my_uc_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    user_id = str(q.from_user.id)
    user = users_data.get(user_id, {})
    amount = user.get("free_uc", 0)
    btn = InlineKeyboardMarkup([
        [InlineKeyboardButton(get_text(user_id, "claim_60"), callback_data="claim_60")],
        [InlineKeyboardButton(get_text(user_id, "claim_325"), callback_data="claim_325")],
    ])
    await q.message.reply_text(get_text(user_id, "my_uc_info", amount=amount), reply_markup=btn)

async def claim_uc_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data
    needed = 60 if data == "claim_60" else 325 if data == "claim_325" else None
    if not needed:
        return
    user_id = str(q.from_user.id)
    user = users_data.get(user_id, {})
    if user.get("free_uc", 0) < needed:
        await q.message.reply_text(get_text(user_id, "not_enough_uc", have=user.get("free_uc", 0)))
        return
    context.user_data["awaiting_free_id"] = needed
    await q.message.reply_text(get_text(user_id, "enter_pubg_id_free"))

async def get_free_uc_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "awaiting_free_id" not in context.user_data:
        return
    t = update.message.text.strip()
    if not t.isdigit() or not (8 <= len(t) <= 15):
        await update.message.reply_text(get_text(update.message.from_user.id, "enter_pubg_id_free"))
        return
    amount = context.user_data.pop("awaiting_free_id")
    user_id = str(update.message.from_user.id)
    user = users_data.get(user_id)
    if not user:
        await update.message.reply_text(get_text(user_id, "not_registered_start"))
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
        "game_id": t,
        "status": "pending",
        "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    orders.append(order)
    save_all()

    for admin in ADMIN_IDS:
        try:
            btn = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("✅ " + get_text(admin, "admin_confirmed"), callback_data=f"admin_confirm_free_{order_id}"),
                    InlineKeyboardButton("❌ " + get_text(admin, "admin_rejected"), callback_data=f"admin_reject_free_{order_id}"),
                ]
            ])
            await context.bot.send_message(
                admin,
                get_text(admin, "free_request_sent", amount=amount, order_id=order_id),
                reply_markup=btn,
            )
        except Exception:
            pass

    await update.message.reply_text(get_text(user_id, "free_request_sent", amount=amount, order_id=order_id))

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
                await q.message.reply_text(f"Фармоиш аллакай дар ҳолати: {o['status']}")
                return
            o["status"] = "confirmed"
            save_all()
            try:
                await context.bot.send_message(int(o["user_id"]), get_text(o["user_id"], "admin_confirmed"))
            except Exception:
                pass
            await q.message.reply_text(get_text(q.from_user.id, "admin_confirmed"))
            return
    await q.message.reply_text(get_text(q.from_user.id, "invalid_order"))

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
                await context.bot.send_message(int(o["user_id"]), get_text(o["user_id"], "admin_rejected"))
            except Exception:
                pass
            await q.message.reply_text(get_text(q.from_user.id, "admin_rejected"))
            return
    await q.message.reply_text(get_text(q.from_user.id, "invalid_order"))

# Admin confirm/reject for paid orders (original flow)
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
                await query.message.reply_text(f"Фармоиш аллакай дар ҳолати: {o['status']}")
                return
            o["status"] = "awaiting_payment"
            save_all()
            try:
                await context.bot.send_message(
                    int(o["user_id"]),
                    f"💳 " + get_text(o["user_id"], "payment_card_info", method="VISA", card=VISA_NUMBER)
                )
            except Exception:
                pass
            await query.message.reply_text(get_text(query.from_user.id, "admin_confirmed"))
            return
    await query.message.reply_text(get_text(query.from_user.id, "invalid_order"))

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
                await query.message.reply_text(f"Фармоиш аллакай дар ҳолати: {o['status']}")
                return
            o["status"] = "rejected"
            save_all()
            try:
                await context.bot.send_message(int(o["user_id"]), get_text(o["user_id"], "admin_rejected"))
            except Exception:
                pass
            await query.message.reply_text(get_text(query.from_user.id, "admin_rejected"))
            return
    await query.message.reply_text(get_text(query.from_user.id, "invalid_order"))

# Invite link
async def invite_link_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    user = q.from_user
    uid = str(user.id)
    try:
        bot = await context.bot.get_me()
        bot_username = bot.username
    except Exception:
        await q.message.reply_text("⚠️")
        return
    invite_url = f"https://t.me/{bot_username}?start=invite_{uid}"
    await q.message.reply_text(
        "🔗 " + invite_url + "\n\n" + get_text(uid, "invite_friends")
    )

# Admin panel (single implementation)
async def admin_panel_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = str(query.from_user.id)

    if data == "admin_panel":
        keyboard = [
            [InlineKeyboardButton(get_text(user_id, "catalog"), callback_data="admin_users")],
            [InlineKeyboardButton(get_text(user_id, "cart"), callback_data="admin_orders")],
            [InlineKeyboardButton(get_text(user_id, "broadcast_prompt"), callback_data="admin_broadcast")],
            [InlineKeyboardButton("⬅️ " + get_text(user_id, "main_menu_text"), callback_data="back_main")],
        ]
        await query.message.edit_text(
            "*Admin panel*",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return

    if data == "admin_users":
        if not users_data:
            text = "📋 Ҳоло ҳеҷ корбар нест."
        else:
            text = "📋 *Рӯйхати корбарон:*\n\n"
            for uid, u in users_data.items():
                text += f"• {u.get('name','—')} — {u.get('phone','—')} (id: {uid})\n"
        await query.message.edit_text(
            text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ " + get_text(user_id, "admin_panel"), callback_data="admin_panel")]])
        )
        return

    if data == "admin_orders":
        if not orders:
            text = "❗ Ҳоло ҳеҷ заказ нест."
        else:
            text = "📦 *Рӯйхати заказҳо:*\n\n"
            for o in orders:
                text += f"#{o['id']} — @{o.get('username') or o.get('user_name','-')} — {o.get('total', o.get('pack',0))} — {o['status']}\n"
        await query.message.edit_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ " + get_text(user_id, "admin_panel"), callback_data="admin_panel")]]))
        return

    if data == "admin_broadcast":
        broadcast_mode[user_id] = True
        await query.message.edit_text(get_text(user_id, "broadcast_prompt"))
        return

# Text handler
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = str(update.message.from_user.id)

    # Broadcast mode
    if broadcast_mode.get(user_id):
        msg = text
        count = 0
        for uid in list(users_data.keys()):
            try:
                await context.bot.send_message(int(uid), f"📣 {get_text(uid, 'broadcast_prompt')}\n\n{msg}")
                count += 1
            except Exception:
                pass
        await update.message.reply_text(get_text(user_id, "broadcast_sent", count=count))
        broadcast_mode[user_id] = False
        return

    # Menu commands
    if text == get_text(user_id, "catalog"):
        await catalog_handler(update, context)
    elif text == get_text(user_id, "wishlist"):
        await open_wishlist_from_text(update, context)
    elif text == get_text(user_id, "cart"):
        await show_cart_from_text(update, context)
    elif text == get_text(user_id, "info"):
        await update.message.reply_text(ADMIN_INFO_TJ)
    elif text == get_text(user_id, "admin_profile"):
        await update.message.reply_text(
            get_text(user_id, "admin_profile"),
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text(user_id, "admin_profile"), url=f"tg://user?id={ADMIN_IDS[0]}")]]),
        )
    elif text == get_text(user_id, "admin_panel") and int(user_id) in ADMIN_IDS:
        buttons = [
            [InlineKeyboardButton(get_text(user_id, "catalog"), callback_data="admin_users"), InlineKeyboardButton(get_text(user_id, "cart"), callback_data="admin_orders")],
            [InlineKeyboardButton(get_text(user_id, "broadcast_prompt"), callback_data="admin_broadcast")],
            [InlineKeyboardButton("⬅️ " + get_text(user_id, "main_menu_text"), callback_data="back_main")],
        ]
        await update.message.reply_text(get_text(user_id, "admin_panel"), reply_markup=InlineKeyboardMarkup(buttons))
    elif text == get_text(user_id, "free_uc"):
        await free_uc_menu(update, context)
    else:
        await update.message.reply_text(get_text(user_id, "use_menu_buttons"))

# Text router for awaiting inputs
async def text_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("awaiting_game_id"):
        await get_game_id(update, context)
        return
    if "awaiting_free_id" in context.user_data:
        await get_free_uc_id(update, context)
        return
    await handle_text(update, context)

# Callback router
async def callback_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not query or not query.data:
        return
    data = query.data

    # language setting via callback (after registration or via /language)
    if data.startswith("setlang_"):
        code = data.split("_", 1)[1]
        uid = str(query.from_user.id)
        if code in LANG:
            set_user_language(uid, code)
            # reply and then show main menu in user's chosen language
            await query.message.reply_text(get_text(uid, "language_changed", lang_name=LANG_NAMES.get(code, code)))
            # show main menu now that language changed
            try:
                await show_main_menu(query.message.chat, uid)
            except Exception:
                pass
        else:
            await query.message.reply_text("⚠️")
        return

    if data == "language_info":
        uid = str(query.from_user.id)
        await query.message.reply_text(get_text(uid, "language_command_info"))
        return

    # Admin panel shortcuts
    if data in ["admin_panel", "admin_users", "admin_orders", "admin_broadcast", "back_admin"]:
        await admin_panel_main(update, context)
        return

    # Catalog and cart
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

    # Admin store confirm/reject
    elif data.startswith("admin_confirm_"):
        await admin_confirm_callback(update, context)
    elif data.startswith("admin_reject_"):
        await admin_reject_callback(update, context)

    # Payment accept/reject (legacy)
    elif data.startswith("payment_accept_") or data.startswith("payment_reject_"):
        await callback_payment_accept_reject(update, context)

    # NEW: payment method selection (VISA / SBER)
    elif data.startswith("pay_visa_") or data.startswith("pay_sber_"):
        await payment_method_callback(update, context)

    # NEW: admin confirm/reject for proofs
    elif data.startswith("pay_confirm_") or data.startswith("pay_reject_"):
        await admin_payment_verify(update, context)

    # Free UC callbacks
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

# Commands
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(get_text(update.message.from_user.id, "language_command_info"))

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(ADMIN_INFO_TJ)

async def users_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if int(update.message.from_user.id) not in ADMIN_IDS:
        await update.message.reply_text("🚫")
        return
    if not users_data:
        await update.message.reply_text("Ҳеҷ корбар сабт нашудааст.")
        return
    text = "📋 Рӯйхати корбарон:\n\n"
    for u in users_data.values():
        text += f"👤 {u.get('name','—')} — {u.get('phone','—')} (id: {u.get('id')})\n"
    await update.message.reply_text(text)

# /language command - allows users to change language any time (no code edits needed)
async def language_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    uid = str(user.id)
    buttons = []
    for code, name in LANG_NAMES.items():
        buttons.append(InlineKeyboardButton(f"{name}", callback_data=f"setlang_{code}"))
    rows = [buttons[i:i+2] for i in range(0, len(buttons), 2)]
    await update.message.reply_text(get_text(uid, "language_choose_title"), reply_markup=InlineKeyboardMarkup(rows))

# Extra command wrappers
async def catalog_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await catalog_handler(update, context)

async def cart_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await show_cart_from_text(update, context)

async def wishlist_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await open_wishlist_from_text(update, context)

async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(ADMIN_INFO_TJ)

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = int(update.message.from_user.id)
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("🚫 Танҳо админ!")
        return
    buttons = [
        [InlineKeyboardButton(get_text(user_id, "catalog"), callback_data="admin_users"), InlineKeyboardButton(get_text(user_id, "cart"), callback_data="admin_orders")],
        [InlineKeyboardButton(get_text(user_id, "broadcast_prompt"), callback_data="admin_broadcast")],
        [InlineKeyboardButton("⬅️ " + get_text(user_id, "main_menu_text"), callback_data="back_main")],
    ]
    await update.message.reply_text(get_text(user_id, "admin_panel"), reply_markup=InlineKeyboardMarkup(buttons))

# Main

def main():
    if TOKEN == "REPLACE_WITH_YOUR_BOT_TOKEN":
        print(get_text(DEFAULT_LANG, "please_set_token"))
        return

    app = ApplicationBuilder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("about", about_command))
    app.add_handler(CommandHandler("users", users_command))
    app.add_handler(CommandHandler("language", language_command))

    # Extra commands
    app.add_handler(CommandHandler("catalog", catalog_command))
    app.add_handler(CommandHandler("cart", cart_command))
    app.add_handler(CommandHandler("wishlist", wishlist_command))
    app.add_handler(CommandHandler("info", info_command))
    app.add_handler(CommandHandler("admin", admin_command))

    # Contact handler
    app.add_handler(MessageHandler(filters.CONTACT, get_contact))

    # CallbackQuery (single router)
    app.add_handler(CallbackQueryHandler(callback_router))

    # Photos & Documents (payment proofs)
    app.add_handler(MessageHandler((filters.PHOTO | filters.Document.ALL) & (~filters.COMMAND), receive_payment_photo))

    # Text messages
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), text_router))

    print(get_text(DEFAULT_LANG, "bot_started"))
    app.run_polling()


if __name__ == "__main__":
    main()