import os
import requests
from telegram.ext import Updater, CommandHandler

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

def mirror(update, context):
    if not context.args:
        update.message.reply_text("⚠️ Kasih link: /m <url>")
        return

    url = context.args[0]
    update.message.reply_text(f"📥 Downloading: {url}")

    # Tentukan nama file
    filename = url.split("/")[-1] or "downloaded_file"
    r = requests.get(url, stream=True)
    with open(filename, "wb") as f:
        for chunk in r.iter_content(1024):
            f.write(chunk)

    # Ambil server GoFile terbaik
    s = requests.get("https://api.gofile.io/servers").json()
    server = s["data"]["servers"][0]["name"]

    # Upload ke GoFile
    files = {"file": open(filename, "rb")}
    res = requests.post(f"https://{server}.gofile.io/uploadFile", files=files).json()
    if res["status"] == "ok":
        dl = res["data"]["downloadPage"]
        update.message.reply_text(f"✅ Mirror Sukses!\n🔗 {dl}")
    else:
        update.message.reply_text(f"❌ Gagal upload: {res}")

def main():
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("m", mirror))
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
