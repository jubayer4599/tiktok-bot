import telebot
import requests
import time
from telebot.types import InputMediaPhoto
from keep_alive import keep_alive

# ==========================================
# আপনার টেলিগ্রাম বটের টোকেন এখানে দিন
BOT_TOKEN = '8263725802:AAGObUwa_EQYpuWgQMomSnECroIOc1symEE'
# ==========================================

bot = telebot.TeleBot(BOT_TOKEN)
API_URL = "https://www.tikwm.com/api/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

print("✅ Bot system started...")

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    try:
        bot.reply_to(message, "⚡ আমি রেডি! TikTok লিংক দিন।")
    except Exception as e:
        print(f"Error sending welcome: {e}")

@bot.message_handler(func=lambda message: True)
def download_tiktok(message):
    try:
        url = message.text.strip()
        
        if "tiktok.com" not in url:
            bot.reply_to(message, "❌ সঠিক TikTok লিংক দিন।")
            return

        status_msg = bot.reply_to(message, "Wait... প্রসেসিং হচ্ছে ⏳")
        bot.send_chat_action(message.chat.id, 'upload_video')

        try:
            response = requests.get(API_URL, params={"url": url}, headers=HEADERS, timeout=20)
            data = response.json()
        except Exception as e:
            bot.edit_message_text("⚠️ সার্ভার এরর! আবার চেষ্টা করুন।", chat_id=message.chat.id, message_id=status_msg.message_id)
            return

        if data.get("code") == 0:
            video_data = data.get("data")
            
            # ডেটা সংগ্রহ
            title = video_data.get("title", "No Title")
            likes = video_data.get("digg_count", 0)
            views = video_data.get("play_count", 0)
            author = video_data.get("author", {}).get("unique_id", "Unknown")
            images = video_data.get("images")

            # আপনার দেওয়া সুন্দর ফরম্যাট
            caption_text = (
                f"👤 @{author}\n"
                f"╔═════════════════╗\n"
                f"╠ Like ❤️ : {likes:,}\n"
                f"║\n"
                f"╠ Views 👀 : {views:,}\n"
                f"╚═════════════════╝\n"
                f"📝 {title}\n\n"
                f"➥ ➜ ᴘᴏᴡᴇʀ  ʙʏ  ᴊᴜʙᴀʏᴇʀ  ♡ جباير"
            )

            # স্লাইডশো লজিক
            if images and len(images) > 0:
                bot.edit_message_text("📸 ছবি আপলোড হচ্ছে...", chat_id=message.chat.id, message_id=status_msg.message_id)
                media_group = [InputMediaPhoto(img) for img in images[:10]]
                bot.send_media_group(message.chat.id, media_group)
                
                if video_data.get("music"):
                    bot.send_audio(message.chat.id, video_data.get("music"), caption=caption_text)
                
                try: bot.delete_message(message.chat.id, status_msg.message_id)
                except: pass

            # ভিডিও লজিক (বড় ফাইল সাপোর্ট সহ)
            else:
                video_url = video_data.get("play")
                bot.edit_message_text("🚀 ভিডিও আপলোড হচ্ছে...", chat_id=message.chat.id, message_id=status_msg.message_id)
                
                try:
                    bot.send_video(
                        message.chat.id, 
                        video_url, 
                        caption=caption_text,
                        timeout=120
                    )
                    bot.delete_message(message.chat.id, status_msg.message_id)
                except Exception as e:
                    # বড় ফাইলের জন্য ব্যাকআপ লিঙ্ক
                    bot.edit_message_text(f"{caption_text}\n\n⚠️ ভিডিওটি বড় হওয়ায় সরাসরি পাঠানো যায়নি।\n🔗 [ডাউনলোড লিঙ্ক]({video_url})", 
                                         chat_id=message.chat.id, message_id=status_msg.message_id, parse_mode="Markdown")

        else:
            bot.edit_message_text("❌ ভিডিও পাওয়া যায়নি।", chat_id=message.chat.id, message_id=status_msg.message_id)

    except Exception as e:
        print(f"Error: {e}")
        try: bot.reply_to(message, "⚠️ সমস্যা হয়েছে, আবার চেষ্টা করুন।")
        except: pass

if __name__ == "__main__":
    keep_alive()
    while True:
        try:
            print("🚀 Bot connecting...")
            bot.infinity_polling(timeout=10, long_polling_timeout=5)
        except Exception as e:
            print(f"❌ Restarting... Error: {e}")
            time.sleep(5)
