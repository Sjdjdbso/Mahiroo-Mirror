import os
import requests
import subprocess
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GOFILE_API_KEY = os.getenv("GOFILE_API_KEY")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")  # isi jika mau notif ke grup

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Halo! Kirim link dan reply dengan /m untuk mirror ke GoFile 🚀")

async def mirror(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message or not update.message.reply_to_message.text:
        await update.message.reply_text("Reply ke pesan yang ada link ya!")
        return

    url = update.message.reply_to_message.text.strip()
    await update.message.reply_text(f"📥 Downloading via aria2c...\n`{url}`")

    # Download pakai aria2c turbo
    filename = "downloaded_file"
    subprocess.run(["aria2c", "-x", "16", "-s", "16", "-o", filename, url], check=True)

    # Upload ke Gofile
    await update.message.reply_text("📤 Uploading to GoFile...")
    files = {"file": open(filename, "rb")}
    r = requests.post("https://store1.gofile.io/uploadFile", files=files)
    res = r.json()

    if res["status"] == "ok":
        link = res["data"]["downloadPage"]
        await update.message.reply_text(f"✅ Done! [Download]({link})", parse_mode="Markdown")
    else:
        await update.message.reply_text("❌ Upload gagal!")

async def notify_start():
    if CHAT_ID:
        requests.get(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                     params={"chat_id": CHAT_ID, "text": "🤖 Bot Mirror baru saja direstart dan siap digunakan!"})

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("m", mirror))
    notify_start()
    app.run_polling()

if __name__ == "__main__":
    main()
