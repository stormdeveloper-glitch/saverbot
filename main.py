import os
import asyncio
import yt_dlp
from pyrogram import Client, filters, types
from pyrogram.errors import UserNotParticipant
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import API_ID, API_HASH, BOT_TOKEN, SESSION_STRING, CHANNELS

# Clientlarni sozlash
bot = Client("saver_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
user_bot = Client("saver_user", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)

# Yuklash funksiyasi
def download_media(url, format_id):
    if not os.path.exists("downloads"):
        os.makedirs("downloads")
    
    ydl_opts = {
        'format': f'{format_id}+bestaudio/best' if format_id != "mp3" else 'bestaudio/best',
        'outtmpl': 'downloads/%(id)s.%(ext)s',
        'noplaylist': True,
        'quiet': True,
        'cookiefile': 'cookies.txt' if os.path.exists('cookies.txt') else None,
        'merge_output_format': 'mp4' if format_id != "mp3" else None,
    }
    
    if format_id == "mp3":
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        path = ydl.prepare_filename(info)
        if format_id == "mp3":
            path = os.path.splitext(path)[0] + ".mp3"
        return path

# Obuna tekshirish
async def is_subscribed(user_id):
    for channel in CHANNELS:
        if not channel:
            continue
        try:
            await bot.get_chat_member(channel.strip(), user_id)
        except UserNotParticipant:
            return channel
        except Exception:
            continue
    return None

@bot.on_message(filters.private & filters.regex(r"http"))
async def on_link(client, message):
    must_sub = await is_subscribed(message.from_user.id)
    if must_sub:
        btn = InlineKeyboardMarkup([[
            InlineKeyboardButton("Obuna bo'lish 📢", url=f"https://t.me/{must_sub.replace('@', '')}")
        ]])
        return await message.reply(f"Botdan foydalanish uchun {must_sub} kanaliga a'zo bo'ling!", reply_markup=btn)

    kb = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🎬 360p", callback_data=f"dl|18|{message.text}"),
            InlineKeyboardButton("🎬 720p", callback_data=f"dl|22|{message.text}")
        ],
        [InlineKeyboardButton("🎵 MP3", callback_data=f"dl|mp3|{message.text}")]
    ])
    await message.reply("Sifatni tanlang va yuklashni boshlang:", reply_markup=kb)

@bot.on_callback_query(filters.regex(r"^dl\|"))
async def handle_callback(client, callback):
    # URL ichida | bo'lishi mumkin, shuning uchun maxsplit=2
    parts = callback.data.split("|", 2)
    _, f_id, url = parts

    status = await callback.message.edit_text("Tayyorlanmoqda... ⏳")
    
    try:
        await status.edit_text("Serverga yuklanmoqda... 📥")
        path = await asyncio.to_thread(download_media, url, f_id)
        
        await status.edit_text("Telegramga yuborilmoqda... 📤")
        
        if f_id == "mp3":
            await user_bot.send_audio(callback.message.chat.id, audio=path, caption="✅ @SizningBot")
        else:
            await user_bot.send_video(callback.message.chat.id, video=path, caption="✅ @SizningBot")
        
        if os.path.exists(path):
            os.remove(path)
        await status.delete()

    except Exception as e:
        await status.edit_text(f"Xatolik yuz berdi: {str(e)[:100]}...")

async def main():
    await user_bot.start()
    await bot.start()
    print("Bot va Userbot muvaffaqiyatli ishga tushdi!")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
