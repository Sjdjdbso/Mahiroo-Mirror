from telegram import Update
from telegram.ext import ContextTypes
import requests
import subprocess

async def mirror(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message or not update.message.reply_to_message.text:
        await update.message.reply_text("Reply ke pesan yang ada link ya!")
        return

    url = update.message.reply_to_message.text.strip()
    await update.message.reply_text(f"📥 Downloading via aria2c...\n`{url}`")

    # Ambil nama file dari header Content-Disposition
    head = requests.head(url, allow_redirects=True)
    cd = head.headers.get("content-disposition")
    if cd and "filename=" in cd:
        filename = cd.split("filename=")[-1].strip('"')
    else:
        filename = url.split("/")[-1] or "downloaded_file"

    # Download turbo pakai aria2c
    subprocess.run(["aria2c", "-x", "16", "-s", "16", "-o", filename, url], check=True)

    # Upload ke GoFile
    await update.message.reply_text("📤 Uploading to GoFile...")
    files = {"file": open(filename, "rb")}
    r = requests.post("https://store1.gofile.io/uploadFile", files=files)
    res = r.json()

    if res["status"] == "ok":
        link = res["data"]["downloadPage"]
        await update.message.reply_text(f"✅ Done! [Download]({link})", parse_mode="Markdown")
    else:
        await update.message.reply_text("❌ Upload gagal!")