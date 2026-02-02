import telebot
import requests
import time
from telebot.types import InputMediaPhoto
from keep_alive import keep_alive

# ==========================================
# আপনার টেলিগ্রাম বটের টোকেন এখানে দিন
BOT_TOKEN = '8450856906:AAHO5RMn0fpmPJ78aZMFtToWHlXYLFyeqJQ'
# ==========================================

bot = telebot.TeleBot(BOT_TOKEN)
API_URL = "https://www.tikwm.com/api/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

print("✅ Bot system is active...")

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    try:
        # সুন্দর লিস্ট ডিজাইন
        welcome_text = (
            "👋 **স্বাগতম! আমি একটি প্রিমিয়াম টিকটক ভিডিও অডিও ফটো কেপশন ডাউনলোডার বট।**\n\n"
            "🚀 **আমার ক্ষমতা বা ফিচারের তালিকা:**\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "✅ **Watermark Removal:** লোগো ছাড়া ফ্রেশ ভিডিও।\n"
            "📸 **Slideshow Support:** স্লাইডশো থেকে ছবি ডাউনলোড।\n"
            "🎵 **Audio Extract:** ভিডিও থেকে MP3 সংগ্রহ।\n"
            "📊 **Real-time Stats:** লাইক এবং ভিউস সংখ্যা দেখা।\n"
            "⚡ **High Speed:** সুপার ফাস্ট প্রসেসিং ও ডেলিভারি।\n"
            "📂 **Large Files:** বড় সাইজ ভিডিও সাপোর্ট।\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "💡 **ব্যবহার নিয়ম:** শুধু একটি TikTok ভিডিও লিংক পাঠান।\n\n"
            "➥ ᴘᴏᴡᴇʀ  ʙʏ  ᴊᴜʙᴀʏᴇʀ  ♡ جباير"
        )
        bot.send_chat_action(message.chat.id, 'typing')
        bot.reply_to(message, welcome_text, parse_mode="Markdown")
    except Exception as e:
        print(f"Error: {e}")

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

            # ক্যাপশন লিমিট ফিক্স
            if len(title) > 800:
                title = title[:800] + "..."

            # আপনার ডিজাইন
            caption_text = (
                f"👤ᴛɪᴋᴛᴏᴋ: @{author}\n"
                f"╔═══════════════╗\n"
                f"╠ ʟɪᴋᴇ ❤️: {likes:,}\n"
                f"║\n"
                f"╠ ᴠɪᴇᴡs 👀: {views:,}\n"
                f"╚═══════════════╝\n"
                f"📝 {title}\n\n"
                f"➥ ᴘᴏᴡᴇʀ  ʙʏ @jubayer3501"
            )

            # স্লাইডশো লজিক
            if images and len(images) > 0:
                bot.edit_message_text("📸 ছবি আপলোড হচ্ছে...", chat_id=message.chat.id, message_id=status_msg.message_id)
                media_group = [InputMediaPhoto(img) for img in images[:10]]
                media_group[0].caption = caption_text
                bot.send_media_group(message.chat.id, media_group)
                
                if video_data.get("music"):
                    bot.send_audio(message.chat.id, video_data.get("music"), caption=f"🎵 Music for @{author}")
                
                try: bot.delete_message(message.chat.id, status_msg.message_id)
                except: pass

            # ভিডিও লজিক
            else:
                video_url = video_data.get("play")
                bot.edit_message_text("🚀 ভিডিও আপলোড হচ্ছে...", chat_id=message.chat.id, message_id=status_msg.message_id)
                
                try:
                    bot.send_video(
                        message.chat.id, 
                        video_url, 
                        caption=caption_text,
                        timeout=150
                    )
                    bot.delete_message(message.chat.id, status_msg.message_id)
                except Exception as e:
                    bot.edit_message_text(f"{caption_text}\n\n🔗 [Download Link]({video_url})", 
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
            bot.infinity_polling(timeout=20, long_polling_timeout=10)
        except Exception as e:
            time.sleep(5)
