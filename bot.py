import os
import requests
import shutil
import tarfile
import zipfile
import subprocess
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GOFILE_API = "https://api.gofile.io"

# Folder kerja
DOWNLOAD_DIR = "downloads"
EXTRACT_DIR = "extracted"

os.makedirs(DOWNLOAD_DIR, exist_ok=True)
os.makedirs(EXTRACT_DIR, exist_ok=True)

def clean_old_files():
    shutil.rmtree(DOWNLOAD_DIR, ignore_errors=True)
    shutil.rmtree(EXTRACT_DIR, ignore_errors=True)
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    os.makedirs(EXTRACT_DIR, exist_ok=True)

def extract_file(filepath):
    extracted_path = os.path.join(EXTRACT_DIR, os.path.splitext(os.path.basename(filepath))[0])
    os.makedirs(extracted_path, exist_ok=True)

    if filepath.endswith(".zip"):
        with zipfile.ZipFile(filepath, 'r') as zip_ref:
            zip_ref.extractall(extracted_path)
    elif filepath.endswith(".tar.gz") or filepath.endswith(".tgz") or filepath.endswith(".tar"):
        with tarfile.open(filepath, 'r:*') as tar_ref:
            tar_ref.extractall(extracted_path)
    else:
        return None
    return extracted_path

def upload_to_gofile(filepath):
    with open(filepath, 'rb') as f:
        r = requests.post(f"{GOFILE_API}/uploadFile", files={"file": f})
    return r.json()["data"]["downloadPage"]

async def mirror(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ Harap beri link!\nContoh: /m https://contoh.com/file.zip")
        return

    url = context.args[0]
    await update.message.reply_text(f"⬇️ Downloading: {url}")

    clean_old_files()

    filename = os.path.join(DOWNLOAD_DIR, os.path.basename(url.split("?")[0]))
    subprocess.run(["aria2c", "-x16", "-s16", "-o", os.path.basename(filename), "-d", DOWNLOAD_DIR, url], check=True)

    context.user_data["downloaded_file"] = filename

    # Kirim tombol pilihan
    keyboard = [
        [InlineKeyboardButton("📤 Upload Normal", callback_data="upload_normal")],
        [InlineKeyboardButton("📂 Extract & Upload", callback_data="upload_extract")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(f"✅ File siap diupload: {os.path.basename(filename)}", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    file_path = context.user_data.get("downloaded_file")
    if not file_path:
        await query.edit_message_text("⚠️ File tidak ditemukan. Ulangi /m <link>")
        return

    choice = query.data
    target = file_path

    if choice == "upload_extract":
        await query.edit_message_text("📂 Mengekstrak file...")
        extracted = extract_file(file_path)
        if extracted:
            shutil.make_archive(extracted, 'zip', extracted)
            target = f"{extracted}.zip"

    await query.edit_message_text("📤 Uploading ke GoFile...")
    link = upload_to_gofile(target)

    await query.edit_message_text(f"✅ Done!\n🔗 {link}")
    clean_old_files()

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("m", mirror))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.run_polling()

if __name__ == "__main__":
    main()