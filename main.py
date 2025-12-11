import os
import re
import yt_dlp
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, ContextTypes, filters

BOT_TOKEN = "7992642305:AAFMfdyjqKxO8uEl61_Z-5-CTXsq89DKNlc"

BAD_WORDS = ["ahmoq", "telba", "jinni", "idiot", "stupid"]

# Cookies fayli joylashgan joy
COOKIES_FILE = "cookies.txt"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Salom! Video yuklab beruvchi bot ishga tushdi.")

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    text = update.message.text

    # 🚫 Taqiqlangan so'zlarni almashtirish
    clean_text = text
    for word in BAD_WORDS:
        clean_text = re.sub(rf"\b{word}\b", "❌", clean_text, flags=re.IGNORECASE)

    if clean_text != text:
        await update.message.delete()
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"{update.effective_user.first_name} xabari tozalandi: {clean_text}"
        )
        return

    # videoni aniqlash
    link_regex = r"(https?://[^\s]+)"
    match = re.search(link_regex, text)
    if not match:
        return

    url = match.group(0)

    # User xabarini o‘chirish
    await update.message.delete()

    # Userga javob berish
    processing_msg = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="📥 Video yuklanmoqda..."
    )

    try:
        # YTDLP opsiyalari
        ydl_opts = {
            'format': 'best',
            'outtmpl': 'video.mp4',
            'quiet': True,
            'cookies': COOKIES_FILE,  # cookies.txt ishlatamiz
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # Video yuborish va user nomini caption'da ko‘rsatish
        user_mention = update.effective_user.mention_html()
        await context.bot.send_video(
            chat_id=update.effective_chat.id,
            video=open("video.mp4", "rb"),
            caption=f"🎬 Video yuklandi!\n👤 {user_mention} tomonidan yuborildi",
            parse_mode="HTML"
        )

        os.remove("video.mp4")
        await processing_msg.delete()

    except Exception as e:
        print("Xato:", e)
        await processing_msg.edit_text("❌ Videoni yuklab bo‘lmadi!")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
    print("Bot ishga tushdi...")
    app.run_polling()

if __name__ == "__main__":
    main()
