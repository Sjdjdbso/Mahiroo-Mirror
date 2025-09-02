import os
import subprocess
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN") or "ISI_TOKEN_MU_DISINI"

async def mirror(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message or not update.message.reply_to_message.text:
        await update.message.reply_text("Reply ke pesan yang ada link ya!")
        return

    url = update.message.reply_to_message.text.strip()
    await update.message.reply_text(f"📥 Mirror Use Aria2c...\n`{url}`")

    # Ambil nama file dari header Content-Disposition
    head = requests.head(url, allow_redirects=True)
    cd = head.headers.get("content-disposition")
    if cd and "filename=" in cd:
        filename = cd.split("filename=")[-1].strip('"')
    else:
        filename = url.split("/")[-1] or "downloaded_file"

    # Download pakai aria2c
    subprocess.run(["aria2c", "-x", "16", "-s", "16", "-o", filename, url], check=True)

    # Upload ke GoFile
    await update.message.reply_text("📤 Uploading...")
    files = {"file": open(filename, "rb")}
    r = requests.post("https://store1.gofile.io/uploadFile", files=files)
    res = r.json()

    if res["status"] == "ok":
        link = res["data"]["downloadPage"]
        await update.message.reply_text(f"✅ Done! [Download]({link})", parse_mode="Markdown")
    else:
        await update.message.reply_text("❌ Upload gagal!")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Halo! Reply pesan link dan ketik /mirror atau /m untuk mulai mirror.")

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Command handler
    app.add_handler(CommandHandler(["start"], start))
    app.add_handler(CommandHandler(["mirror", "m"], mirror))  # <-- /mirror dan /m

    print("Bot jalan...")
    app.run_polling()

if __name__ == "__main__":
    main()