import telebot
import requests
import time
import sys
from threading import Thread
from telebot.types import InputMediaPhoto
from keep_alive import keep_alive

# ==========================================
# আপনার টেলিগ্রাম বটের টোকেন
BOT_TOKEN = 'YOUR_BOT_TOKEN_HERE'
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
        
        # লিংক চেক করা
        if "tiktok.com" not in url:
            bot.reply_to(message, "❌ সঠিক TikTok লিংক দিন।")
            return

        status_msg = bot.reply_to(message, "Wait... প্রসেসিং হচ্ছে ⏳")
        bot.send_chat_action(message.chat.id, 'upload_video')

        # API কল (টাইমআউট সহ)
        try:
            response = requests.get(API_URL, params={"url": url}, headers=HEADERS, timeout=20)
            data = response.json()
        except requests.exceptions.RequestException as e:
            bot.edit_message_text("⚠️ সার্ভার থেকে ডেটা পাওয়া যাচ্ছে না। আবার চেষ্টা করুন।", chat_id=message.chat.id, message_id=status_msg.message_id)
            print(f"Network Error: {e}")
            return

        if data.get("code") == 0:
            video_data = data.get("data")
            title = video_data.get("title", "No Caption")
            images = video_data.get("images")

            # স্লাইডশো লজিক
            if images and len(images) > 0:
                bot.edit_message_text("📸 ছবি আপলোড হচ্ছে...", chat_id=message.chat.id, message_id=status_msg.message_id)
                media_group = [InputMediaPhoto(img) for img in images[:10]]
                bot.send_media_group(message.chat.id, media_group)
                
                if video_data.get("music"):
                    bot.send_audio(message.chat.id, video_data.get("music"))
                
                try:
                    bot.delete_message(message.chat.id, status_msg.message_id)
                except:
                    pass

            # ভিডিও লজিক
            else:
                video_url = video_data.get("play")
                bot.edit_message_text("🚀 ভিডিও আপলোড হচ্ছে...", chat_id=message.chat.id, message_id=status_msg.message_id)
                
                try:
                    bot.send_video(
                        message.chat.id, 
                        video_url, 
                        caption=f"📝 {title}", 
                        parse_mode="Markdown"
                    )
                    bot.delete_message(message.chat.id, status_msg.message_id)
                except Exception as e:
                    bot.edit_message_text("❌ ভিডিও পাঠানো যায়নি (File too large or Telegram Error).", chat_id=message.chat.id, message_id=status_msg.message_id)
                    print(f"Send Video Error: {e}")

        else:
            bot.edit_message_text("❌ ভিডিও পাওয়া যায়নি। লিংক চেক করুন।", chat_id=message.chat.id, message_id=status_msg.message_id)

    except Exception as e:
        print(f"Critical Error in handler: {e}")
        # ক্র্যাশ না করে ইউজারকে জানানো
        try:
            bot.reply_to(message, "⚠️ একটি অজানা সমস্যা হয়েছে। দয়া করে আবার লিংক দিন।")
        except:
            pass

# --- সার্ভার রান এবং রিকানেক্ট লজিক ---
if __name__ == "__main__":
    keep_alive() # সার্ভার জাগিয়ে রাখা
    
    # এই লুপটি বটকে মরতে দিবে না
    while True:
        try:
            print("🚀 Bot connecting to Telegram...")
            # timeout এবং long_polling_timeout ব্যবহার করা হয়েছে কানেকশন স্টেবল রাখার জন্য
            bot.infinity_polling(timeout=10, long_polling_timeout=5)
        except Exception as e:
            print(f"❌ Bot Crashed! Restarting in 5 seconds... Error: {e}")
            time.sleep(5) # ৫ সেকেন্ড বিশ্রাম নিয়ে আবার চালু হবে
