import requests
import base64
from io import BytesIO
from PIL import Image
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# ========== ТАНЗИМ ==========
TELEGRAM_TOKEN = "8349272439:AAGP_QB7BAArE3KlsMph_C9Izx94pPuigok"
STABILITY_API_KEY = "sk-ye5sr3Ozirw8cdHc40LpXzRgCYLXnQUcnsfvAIPrN60zvJTD"

STABILITY_URL = "https://api.stability.ai/v2beta/stable-image/edit"
# ============================

headers = {
    "Authorization": f"Bearer {STABILITY_API_KEY}"
}

user_mode = {}  # user_id -> "man" or "woman"


def start(update, context):
    update.message.reply_text(
        "👋 Салом!\n\n"
        "📸 Акс фирист\n"
        "➡️ /man — зан → мард\n"
        "➡️ /woman — мард → зан\n\n"
        "ℹ️ Шахсият нигоҳ дошта намешавад"
    )


def set_man(update, context):
    user_mode[update.message.from_user.id] = "man"
    update.message.reply_text("✅ Режим: ЗАН → МАРД")


def set_woman(update, context):
    user_mode[update.message.from_user.id] = "woman"
    update.message.reply_text("✅ Режим: МАРД → ЗАН")


def handle_photo(update, context):
    user_id = update.message.from_user.id
    mode = user_mode.get(user_id)

    if not mode:
        update.message.reply_text("❗ Аввал /man ё /woman-ро интихоб кун")
        return

    photo = update.message.photo[-1]
    file = context.bot.get_file(photo.file_id)
    image_bytes = file.download_as_bytearray()

    prompt = (
        "realistic photo of a man, masculine appearance, same pose and framing, high quality"
        if mode == "man"
        else
        "realistic photo of a woman, feminine appearance, same pose and framing, high quality"
    )

    update.message.reply_text("⏳ Кор карда истодааст...")

    files = {
        "image": image_bytes
    }

    data = {
        "prompt": prompt,
        "strength": 0.6,
        "output_format": "png"
    }

    response = requests.post(
        STABILITY_URL,
        headers=headers,
        files=files,
        data=data,
        timeout=120
    )

    if response.status_code != 200:
        update.message.reply_text("❌ Хато дар API\n" + response.text)
        return

    result = response.json()
    img_base64 = result.get("image")

    if not img_base64:
        update.message.reply_text("❌ Натиҷа барнагашт")
        return

    img_bytes = base64.b64decode(img_base64)
    img = Image.open(BytesIO(img_bytes))
    bio = BytesIO()
    bio.name = "result.png"
    img.save(bio, "PNG")
    bio.seek(0)

    update.message.reply_photo(photo=bio, caption="✅ Тайёр!")


def main():
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("man", set_man))
    dp.add_handler(CommandHandler("woman", set_woman))
    dp.add_handler(MessageHandler(Filters.photo, handle_photo))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()