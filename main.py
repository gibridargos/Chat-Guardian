import os
import re
import yt_dlp
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, ContextTypes, filters

BOT_TOKEN = "7992642305:AAFMfdyjqKxO8uEl61_Z-5-CTXsq89DKNlc"

BAD_WORDS = ["ahmoq", "telba", "jinni", "idiot", "stupid"]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Salom! Video yuklab beruvchi bot ishga tushdi.")

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    # videoni aniqlash
    link_regex = r"(https?://[^\s]+)"
    match = re.search(link_regex, text)

    if not match:
        return

    url = match.group(0)

    await update.message.reply_text("📥 Video yuklanmoqda...")

    try:
        # YTDLP opsiya
        ydl_opts = {
            'format': 'best',
            'outtmpl': 'video.mp4',
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # Telegramga video jo‘natish
        await update.message.reply_video(
            video=open("video.mp4", "rb"),
            caption="🎬 Video tayyor!"
        )

        os.remove("video.mp4")

    except Exception as e:
        print("Xato:", e)
        await update.message.reply_text("❌ Videoni yuklab bo‘lmadi!")

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

    print("Bot ishga tushdi...")
    app.run_polling()

if __name__ == "__main__":
    main()
