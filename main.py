import telebot
import requests
import time
import sys
import os
from threading import Thread
from telebot.types import InputMediaPhoto
from keep_alive import keep_alive

# ==========================================
# আপনার টেলিগ্রাম বটের টোকেন
BOT_TOKEN = '8263725802:AAGObUwa_EQYpuWgQMomSnECroIOc1symEE'
# ==========================================

bot = telebot.TeleBot(BOT_TOKEN)
API_URL = "https://www.tikwm.com/api"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Origin": "https://www.tikwm.com",
    "Referer": "https://www.tikwm.com/",
    "Connection": "keep-alive"
}

print("✅ Bot system started...")

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    try:
        bot.reply_to(message, "⚡ আমি রেডি! TikTok লিংক দিন।\n\n📌 লিমিট ছাড়াই ডাউনলোড!")
    except Exception as e:
        print(f"Error sending welcome: {e}")

@bot.message_handler(func=lambda message: True)
def download_tiktok(message):
    try:
        url = message.text.strip()
        
        # লিংক চেক করা - সব TikTok ডোমেইন সাপোর্ট করে
        tiktok_domains = ['tiktok.com', 'vt.tiktok.com', 'vm.tiktok.com']
        if not any(domain in url for domain in tiktok_domains):
            bot.reply_to(message, "❌ সঠিক TikTok লিংক দিন।")
            return

        status_msg = bot.reply_to(message, "⏳ লিমিট ছাড়াই প্রসেসিং হচ্ছে...")
        bot.send_chat_action(message.chat.id, 'upload_video')

        # API কল (টাইমআউট সহ) - লিমিট ছাড়াই
        try:
            # প্রথমে API থেকে ডাটা নিন
            response = requests.post(
                "https://www.tikwm.com/api/",
                data={"url": url},
                headers=HEADERS,
                timeout=30
            )
            data = response.json()
            
            # যদি প্রথম API কাজ না করে, বিকল্প API ব্যবহার করুন
            if data.get("code") != 0:
                # বিকল্প API 1
                alt_response = requests.get(
                    "https://tikwm.com/api/",
                    params={"url": url},
                    headers=HEADERS,
                    timeout=30
                )
                data = alt_response.json()
                
        except requests.exceptions.RequestException as e:
            bot.edit_message_text(
                "⚠️ সার্ভার থেকে ডেটা পাওয়া যাচ্ছে না। আবার চেষ্টা করুন।", 
                chat_id=message.chat.id, 
                message_id=status_msg.message_id
            )
            print(f"Network Error: {e}")
            return

        if data.get("code") == 0:
            video_data = data.get("data", {})
            title = video_data.get("title", "No Caption")
            images = video_data.get("images", [])
            
            # ভিডিও লিংক পাওয়া (HD,无水印 - লিমিট ছাড়া)
            video_url = video_data.get("play", "")
            hd_video_url = video_data.get("hdplay", "")  # HD লিংক
            
            # লিমিট ছাড়া ভিডিও লিংক প্রায়োরিটি
            final_video_url = hd_video_url if hd_video_url else video_url
            
            # মিউজিক লিংক
            music_url = video_data.get("music", "")
            
            # স্লাইডশো লজিক (ছবি)
            if images and len(images) > 0:
                bot.edit_message_text(
                    "📸 লিমিট ছাড়া ছবি আপলোড হচ্ছে...", 
                    chat_id=message.chat.id, 
                    message_id=status_msg.message_id
                )
                
                # ছবিগুলো গ্রুপে পাঠানো
                try:
                    media_group = [InputMediaPhoto(img) for img in images]
                    
                    # ছবিগুলোকে 10টি করে গ্রুপে ভাগ করা (টেলিগ্রামের লিমিট)
                    for i in range(0, len(media_group), 10):
                        bot.send_media_group(
                            message.chat.id, 
                            media_group[i:i+10]
                        )
                except Exception as e:
                    print(f"Error sending images: {e}")
                    # যদি গ্রুপে পাঠানো না যায়, তাহলে আলাদা আলাদা
                    for img in images[:10]:
                        try:
                            bot.send_photo(message.chat.id, img)
                        except:
                            pass
                
                # মিউজিক থাকলে পাঠানো
                if music_url:
                    try:
                        bot.send_audio(message.chat.id, music_url, caption="🎵 TikTok Music")
                    except:
                        pass
                
                try:
                    bot.delete_message(message.chat.id, status_msg.message_id)
                except:
                    pass
                    
            # ভিডিও লজিক (লিমিট ছাড়া)
            elif final_video_url:
                bot.edit_message_text(
                    "🚀 লিমিট ছাড়া ভিডিও প্রসেসিং হচ্ছে...", 
                    chat_id=message.chat.id, 
                    message_id=status_msg.message_id
                )
                
                try:
                    # লিমিট ছাড়া ভিডিও পাঠানোর চেষ্টা
                    # প্রথমে direct URL দিয়ে চেষ্টা
                    bot.send_video(
                        message.chat.id, 
                        final_video_url,
                        caption=f"🎬 **লিমিট ছাড়া TikTok ভিডিও**\n\n{title}",
                        parse_mode="Markdown",
                        timeout=300,
                        supports_streaming=True
                    )
                    
                    try:
                        bot.delete_message(message.chat.id, status_msg.message_id)
                    except:
                        pass
                        
                except Exception as e:
                    print(f"Send Video Error: {e}")
                    
                    # বিকল্প পদ্ধতি 1: ফাইল হিসেবে পাঠানো
                    try:
                        # ভিডিও ডাউনলোড করে ফাইল হিসেবে পাঠানো
                        bot.edit_message_text(
                            "⬇️ ভিডিও ডাউনলোড হচ্ছে...", 
                            chat_id=message.chat.id, 
                            message_id=status_msg.message_id
                        )
                        
                        # টেম্পোরারি ফাইল ডাউনলোড
                        video_response = requests.get(final_video_url, timeout=60)
                        
                        if video_response.status_code == 200:
                            # টেম্পোরারি ফাইল সেভ করা
                            temp_filename = f"temp_video_{message.message_id}.mp4"
                            with open(temp_filename, 'wb') as f:
                                f.write(video_response.content)
                            
                            # ফাইল হিসেবে পাঠানো
                            with open(temp_filename, 'rb') as video_file:
                                bot.send_video(
                                    message.chat.id,
                                    video_file,
                                    caption=f"🎬 **লিমিট ছাড়া TikTok ভিডিও**\n\n{title}",
                                    parse_mode="Markdown",
                                    timeout=300,
                                    supports_streaming=True
                                )
                            
                            # টেম্পোরারি ফাইল ডিলিট করা
                            if os.path.exists(temp_filename):
                                os.remove(temp_filename)
                                
                            try:
                                bot.delete_message(message.chat.id, status_msg.message_id)
                            except:
                                pass
                        else:
                            raise Exception("Failed to download video")
                            
                    except Exception as e2:
                        print(f"Alternative method error: {e2}")
                        
                        # চূড়ান্ত বিকল্প: লিংক পাঠানো
                        bot.edit_message_text(
                            f"🎬 **লিমিট ছাড়া TikTok ভিডিও**\n\n{title}\n\n"
                            f"🔗 **HD Video Link:** [Click to Download]({final_video_url})\n"
                            f"🔗 **Music Link:** [Click Here]({music_url})" if music_url else "",
                            chat_id=message.chat.id, 
                            message_id=status_msg.message_id,
                            parse_mode="Markdown"
                        )
            else:
                bot.edit_message_text(
                    "❌ ভিডিও লিংক পাওয়া যায়নি।", 
                    chat_id=message.chat.id, 
                    message_id=status_msg.message_id
                )
        else:
            error_msg = data.get("msg", "Unknown error")
            bot.edit_message_text(
                f"❌ ত্রুটি: {error_msg}\n\n🔧 লিমিট রিমুভ করার চেষ্টা করছি...", 
                chat_id=message.chat.id, 
                message_id=status_msg.message_id
            )
            
            # বিকল্প API চেষ্টা
            try:
                bot.send_message(
                    message.chat.id,
                    "🔄 লিমিট রিমুভ করার জন্য বিকল্প মেথড ব্যবহার করছি...",
                    reply_to_message_id=message.message_id
                )
                
                # Alternative TikTok downloader APIs without limits
                alt_apis = [
                    "https://api.tikmate.app/download",
                    "https://api.qewertyy.dev/download/tiktok",
                    "https://lovetik.com/api/ajaxSearch"
                ]
                
                for api in alt_apis:
                    try:
                        response = requests.post(api, data={"url": url}, timeout=20)
                        if response.status_code == 200:
                            bot.send_message(message.chat.id, f"✅ Alternative API worked: {api}")
                            break
                    except:
                        continue
                        
            except Exception as alt_e:
                print(f"Alternative API error: {alt_e}")
            
    except Exception as e:
        print(f"General Error: {e}")
        try:
            bot.reply_to(message, f"❌ ত্রুটি হয়েছে: {str(e)[:200]}")
        except:
            pass

# লিমিট ছাড়া ডাউনলোডের জন্য বিশেষ ফাংশন
def download_without_limits(url):
    """লিমিট ছাড়া TikTok ভিডিও ডাউনলোড"""
    try:
        # Multiple API endpoints to bypass limits
        apis = [
            {"url": "https://www.tikwm.com/api/", "method": "POST"},
            {"url": "https://tikwm.com/api/", "method": "GET"},
            {"url": "https://api.tikmate.app/download", "method": "POST"},
        ]
        
        for api in apis:
            try:
                if api["method"] == "POST":
                    response = requests.post(api["url"], data={"url": url}, timeout=30)
                else:
                    response = requests.get(api["url"], params={"url": url}, timeout=30)
                
                if response.status_code == 200:
                    return response.json()
            except:
                continue
        
        return None
    except Exception as e:
        print(f"Download without limits error: {e}")
        return None

# ব্যাকগ্রাউন্ডে চালানোর জন্য
def run_bot():
    try:
        print("🤖 Bot polling started...")
        bot.polling(none_stop=True, interval=0, timeout=60)
    except Exception as e:
        print(f"Bot polling error: {e}")
        time.sleep(10)
        run_bot()

if __name__ == "__main__":
    # ব্যাকগ্রাউন্ড টাস্ক শুরু করুন
    Thread(target=keep_alive).start()
    time.sleep(3)
    # বট চালু করুন
    print("🔥 লিমিট ছাড়া TikTok Downloader চালু!")
    run_bot()
