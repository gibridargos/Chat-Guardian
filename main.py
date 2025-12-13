import os
import re
import yt_dlp
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    Application,
    MessageHandler,
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler,
    filters
)

BOT_TOKEN = "7992642305:AAFMfdyjqKxO8uEl61_Z-5-CTXsq89DKNlc"

BAD_WORDS = ["ahmoq", "telba", "jinni", "idiot", "stupid"]
COOKIES_FILE = "cookies.txt"

LINK_REGEX = r"(https?://[^\s]+)"
YOUTUBE_REGEX = r"(youtube\.com|youtu\.be)"


# ================= /START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user

    # ===== PRIVATE =====
    if chat.type == "private":
        keyboard = [
            [
                InlineKeyboardButton(
                    "➕ Guruhga qo‘shish",
                    url=f"https://t.me/{context.bot.username}?startgroup=true"
                )
            ],
            [
                InlineKeyboardButton(
                    "📥 Video yuborish",
                    callback_data="send_video"
                )
            ]
        ]

        await update.message.reply_text(
            "👋 <b>Salom!</b>\n\n"
            "📥 Menga video silkani yuboring — video qilib beraman.\n"
            "🚫 So‘kinish va cheklangan so‘zlarni tozalayman.\n"
            "❌ YouTube linklar ishlamaydi.\n\n"
            "👇 Tugmalardan foydalaning:",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # ===== GROUP =====
    elif chat.type in ["group", "supergroup"]:
        member = await context.bot.get_chat_member(chat.id, user.id)

        if member.status in ["administrator", "creator"]:
            await update.message.reply_text(
                "👋 <b>Salom!</b>\n\n"
                "📌 Guruhga video silkani yuboring — men uni video qilib beraman.\n"
                "🚫 So‘kinish va cheklangan so‘zlarni tozalayman.\n"
                "❌ YouTube linklar qo‘llab-quvvatlanmaydi.",
                parse_mode="HTML"
            )


# ================= INLINE BUTTON =================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "send_video":
        await query.message.reply_text(
            "📥 Video silkani yuboring.\n"
            "❌ YouTube linklar ishlamaydi."
        )


# ================= MESSAGE HANDLER =================
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    text = update.message.text

    # 🚫 So‘kinishlarni tekshirish
    clean_text = text
    for word in BAD_WORDS:
        clean_text = re.sub(
            rf"\b{word}\b",
            "❌",
            clean_text,
            flags=re.IGNORECASE
        )

    if clean_text != text:
        await update.message.delete()
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"⚠️ {update.effective_user.first_name} xabari tozalandi:\n{clean_text}"
        )
        return

    # 🔗 Linkni aniqlash
    match = re.search(LINK_REGEX, text)
    if not match:
        return

    url = match.group(0)

    # ❌ YouTube bo‘lsa — e’tibor bermaymiz
    if re.search(YOUTUBE_REGEX, url, re.IGNORECASE):
        return

    # 🗑 User xabarini o‘chirish
    await update.message.delete()

    processing_msg = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="📥 Video yuklanmoqda..."
    )

    try:
        ydl_opts = {
            "format": "best",
            "outtmpl": "video.mp4",
            "quiet": True,
            "cookies": COOKIES_FILE,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        user_mention = update.effective_user.mention_html()

        await context.bot.send_video(
            chat_id=update.effective_chat.id,
            video=open("video.mp4", "rb"),
            caption=(
                "🎬 <b>Video yuklandi!</b>\n"
                f"👤 {user_mention}\n\n"
                f"🔗 <b>Video silkasi:</b>\n{url}"
            ),
            parse_mode="HTML"
        )

        os.remove("video.mp4")
        await processing_msg.delete()

    except Exception as e:
        print("Xato:", e)
        await processing_msg.edit_text("❌ Videoni yuklab bo‘lmadi!")


# ================= MAIN =================
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

    print("🤖 Bot ishga tushdi...")
    app.run_polling()


if __name__ == "__main__":
    main()
