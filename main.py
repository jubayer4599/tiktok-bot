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
                    
                # ভিডিও লজিক (বড় ফাইল সাপোর্ট সহ)
            else:
                video_url = video_data.get("play")
                bot.edit_message_text("🚀 বড় ভিডিও প্রসেসিং হচ্ছে... আপলোড শুরু হয়েছে।", chat_id=message.chat.id, message_id=status_msg.message_id)
                
                try:
                    # ফাইল ডাউনলোড না করে সরাসরি URL ব্যবহার করে পাঠানো (এটি দ্রুত এবং বড় ফাইল সাপোর্ট করে)
                    bot.send_video(
                        message.chat.id, 
                        video_url, 
                        caption=f"📝 {title}", 
                        parse_mode="Markdown",
                        timeout=120 # সার্ভারকে ২ মিনিট সময় দেওয়া হলো আপলোডের জন্য
                    )
                    
                    try:
                        bot.delete_message(message.chat.id, status_msg.message_id)
                    except:
                        pass
                except Exception as e:
                    print(f"Send Video Error: {e}")
                    # যদি URL পদ্ধতিতে কাজ না হয়, তবে টেক্সট লিংক হিসেবে পাঠানো
                    bot.edit_message_text(f"❌ ভিডিওটি সরাসরি পাঠানো সম্ভব হয়নি।\n\n🔗 আপনি এখান থেকে ডাউনলোড করতে পারেন: [Download Link]({video_url})", 
                                         chat_id=message.chat.id, 
                                         message_id=status_msg.message_id, 
                                         parse_mode="Markdown")
