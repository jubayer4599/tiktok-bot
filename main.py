import telebot
import requests
import time
from telebot.types import InputMediaPhoto
from keep_alive import keep_alive  # সার্ভার ফাইল ইম্পোর্ট করা হলো

# ==========================================
BOT_TOKEN = '8263725802:AAGObUwa_EQYpuWgQMomSnECroIOc1symEE'  # <--- আপনার টোকেন এখানে দিন
# ==========================================

bot = telebot.TeleBot(BOT_TOKEN)
API_URL = "https://www.tikwm.com/api/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.send_chat_action(message.chat.id, 'typing')
    bot.reply_to(message, "⚡ আমি রেডি! \nআমাকে একটি TikTok ভিডিওর লিংক দিন।")

@bot.message_handler(func=lambda message: True)
def download_tiktok(message):
    url = message.text.strip()
    if "tiktok.com" not in url:
        bot.reply_to(message, "❌ এটি সঠিক TikTok লিংক নয়।")
        return

    status_msg = bot.reply_to(message, "🔍 ভিডিও প্রসেসিং হচ্ছে...")
    bot.send_chat_action(message.chat.id, 'upload_video')

    try:
        response = requests.get(API_URL, params={"url": url}, headers=HEADERS, timeout=15)
        data = response.json()

        if data.get("code") == 0:
            video_data = data.get("data")
            title = video_data.get("title", "No Caption")
            images = video_data.get("images")

            if images and len(images) > 0:
                bot.edit_message_text("📸 স্লাইডশো আপলোড হচ্ছে...", chat_id=message.chat.id, message_id=status_msg.message_id)
                media_group = [InputMediaPhoto(img) for img in images[:10]]
                bot.send_media_group(message.chat.id, media_group)
                if video_data.get("music"):
                    bot.send_audio(message.chat.id, video_data.get("music"))
            else:
                bot.edit_message_text("🚀 ভিডিও আপলোড হচ্ছে...", chat_id=message.chat.id, message_id=status_msg.message_id)
                bot.send_video(message.chat.id, video_data.get("play"), caption=f"📝 {title}")
            
            bot.delete_message(message.chat.id, status_msg.message_id)
        else:
            bot.edit_message_text("❌ ভিডিও পাওয়া যায়নি।", chat_id=message.chat.id, message_id=status_msg.message_id)
    except Exception as e:
        print(e)
        bot.edit_message_text("⚠️ এরর হয়েছে।", chat_id=message.chat.id, message_id=status_msg.message_id)

# সার্ভার রান করা
if __name__ == "__main__":
    keep_alive()  # ফ্লাস্ক সার্ভার চালু
    bot.infinity_polling(skip_pending=True)
