import os
import re
import yt_dlp
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

BOT_TOKEN = "7992642305:AAFMfdyjqKxO8uEl61_Z-5-CTXsq89DKNlc"

BAD_WORDS = [
    "ahmoq","telba","jinni","sokin","haqorat","axmoq","nodon","la'nat","shayton",
    "it","yaramas","beodob","harom","haromi","bosqinchi","sharshara","lanj",
    "iflos","tentak",
    "дурак","идиот","тупой","баран","осёл","сволочь","тварь","мразь","гнида",
    "ублюдок","мудак","пидор","блядь","сука","шлюха","проститутка","хуй",
    "ебанат","гондон","чмо","дерьмо","козел",
    "idiot","stupid","dumb","fool","loser","bastard","moron",
    "jerk","shit","fuck","fucker","motherfucker","mf",
    "asshole","bitch","whore","slut","dick","cock","pussy",
    "cunt","nigger","retard","gay","fag","faggot","wanker"
]

async def members(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    count = await context.bot.get_chat_member_count(chat.id)
    await update.message.reply_text(f"👥 Guruh a'zolari soni: {count}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    text = update.message.text
    clean_text = text

    for word in BAD_WORDS:
        clean_text = re.sub(rf"\\b{word}\\b", "❌", clean_text, flags=re.IGNORECASE)

    if clean_text != text:
        await update.message.delete()
        await update.message.reply_text(f"{update.effective_user.first_name} xabari tozalandi: {clean_text}")
        return

    link_regex = r"(https?:\\/\\/(?:www\\.)?(instagram\\.com|tiktok\\.com|youtube\\.com|youtu\\.be)[^\\s]+)"
    match = re.search(link_regex, text)

    if match:
        url = match.group(0).split("?")[0]
        try:
            await update.message.reply_text("📥 Yuklanmoqda...")

            opts = {
                "format": "best",
                "quiet": True,
                "noplaylist": True
            }

            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)
                vurl = None

                for f in info["formats"]:
                    if f.get("ext") == "mp4" and f.get("acodec") != "none":
                        vurl = f["url"]
                        break

            if vurl:
                await update.message.reply_video(vurl, caption="🎬 Video yuklandi!")

        except Exception as e:
            print("Xatolik:", e)
            await update.message.reply_text("❌ Video yuklab bo‘lmadi.")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Salom, men guruh moderator botman! 🚀")

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("members", members))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🚀 Railway bot ishga tushdi...")
    app.run_polling()

if __name__ == "__main__":
    main()
