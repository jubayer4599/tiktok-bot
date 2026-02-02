import telebot
import requests
import time
import sys
from threading import Thread
from telebot.types import InputMediaPhoto
from keep_alive import keep_alive

# ==========================================
# আপনার টেলিগ্রাম বটের টোকেন
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
                    
                            # ভিডিও লজিক (লাইক এবং ভিউস সহ)
            else:
                video_url = video_data.get("play")
                
                # লাইক, ভিউস এবং কমেন্ট সংখ্যা নেওয়া
                likes = video_data.get("digg_count", 0)
                views = video_data.get("play_count", 0)
                comments = video_data.get("comment_count", 0)
                
                # সংখ্যাগুলো সুন্দর করে সাজানো (যেমন: 1500 থেকে 1.5K করা যায়, তবে এখানে সরাসরি দেখাচ্ছি)
                stats = f"❤️ Likes: {likes:,} | 👁️ Views: {views:,} | 💬 Comments: {comments:,}"

                bot.edit_message_text("🚀 ভিডিও এবং তথ্য প্রসেসিং হচ্ছে...", chat_id=message.chat.id, message_id=status_msg.message_id)
                
                try:
                    bot.send_video(
                        message.chat.id, 
                        video_url, 
                        caption=f"📝 **{title}**\n\n📊 **Stats:**\n{stats}\n\n✅ Powered by @YourBotUsername", 
                        parse_mode="Markdown",
                        timeout=120
                    )
                    bot.delete_message(message.chat.id, status_msg.message_id)
                except Exception as e:
                    print(f"Send Video Error: {e}")
                    bot.edit_message_text(f"❌ ভিডিও পাঠানো যায়নি।\n\n📊 {stats}\n\n🔗 [Download Link]({video_url})", 
                                         chat_id=message.chat.id, 
                                         message_id=status_msg.message_id, 
                                         parse_mode="Markdown")
