import telebot
import requests
import time
import sys
import os
import random
from threading import Thread
from telebot.types import InputMediaPhoto
from keep_alive import keep_alive

# ==========================================
# আপনার টেলিগ্রাম বটের টোকেন
BOT_TOKEN = '8263725802:AAGObUwa_EQYpuWgQMomSnECroIOc1symEE'
# ==========================================

bot = telebot.TeleBot(BOT_TOKEN)

# লিমিট বাইপাস করার জন্য API লিস্ট
LIMIT_BYPASS_APIS = [
    {"url": "https://www.tikwm.com/api/", "method": "POST", "name": "TikWM"},
    {"url": "https://tikwm.com/api/", "method": "GET", "name": "TikWM Alt"},
    {"url": "https://api.tikmate.app/api/v2/download", "method": "POST", "name": "TikMate"},
    {"url": "https://ssstik.io/abc", "method": "POST", "name": "SSSTik"},
    {"url": "https://musicallydown.com/api/ajaxSearch", "method": "POST", "name": "MusicallyDown"},
    {"url": "https://api.douyin.wtf/api", "method": "GET", "name": "Douyin"},
    {"url": "https://tiktok-video-no-watermark2.p.rapidapi.com/", "method": "GET", "name": "RapidAPI"},
    {"url": "https://tiklydown.eu.org/api/download", "method": "GET", "name": "TiklyDown"},
]

# User Agents রোটেশন (লিমিট এড়ানোর জন্য)
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (iPad; CPU OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
]

# TikTok official APIs (advanced bypass)
TIKTOK_OFFICIAL_APIS = [
    "https://api16-normal-c-useast1a.tiktokv.com/aweme/v1/feed/",
    "https://api19-normal-c-useast1a.tiktokv.com/aweme/v1/feed/",
    "https://api.tiktokv.com/aweme/v1/play/",
    "https://api2-16-h2.musical.ly/aweme/v1/feed/",
]

print("✅ লিমিট বাইপাস TikTok Bot চালু হচ্ছে...")

def get_random_user_agent():
    """র‍্যান্ডম User Agent রিটার্ন করে"""
    return random.choice(USER_AGENTS)

def get_headers():
    """Headers তৈরি করে"""
    return {
        "User-Agent": get_random_user_agent(),
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9,bn;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Origin": "https://www.tiktok.com",
        "Referer": "https://www.tiktok.com/",
        "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "Connection": "keep-alive",
        "DNT": "1",
    }

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    try:
        welcome_text = """
🚀 **লিমিট বাইপাস TikTok Downloader**
        
⚡ আমি TikTok ভিডিও লিমিট ছাড়া ডাউনলোড করি!

📌 **ফিচারসমূহ:**
✅ লিমিট ছাড়া HD ভিডিও
✅ ছবি স্লাইডশো সাপোর্ট
✅ ওয়াটারমার্ক ছাড়া ভিডিও
✅ অডিও আলাদা ডাউনলোড
✅ সম্পূর্ণ ক্যাপশন + ভিউস + লাইকস
✅ সব ধরনের TikTok লিংক

📥 **যেভাবে ব্যবহার করবেন:**
1. TikTok ভিডিও লিংক কপি করুন
2. এই বটে পেস্ট করুন
3. কিছুক্ষণ অপেক্ষা করুন

⚙️ **লিংক ফরম্যাট:**
• https://www.tiktok.com/@user/video/123456789
• https://vm.tiktok.com/abcdefg/
• https://vt.tiktok.com/zyxwvut/

🎯 **লিমিট বাইপাস সক্রিয়!**
        """
        bot.reply_to(message, welcome_text, parse_mode="Markdown")
    except Exception as e:
        print(f"Error sending welcome: {e}")

@bot.message_handler(commands=['status'])
def check_status(message):
    """বটের স্ট্যাটাস চেক"""
    try:
        status_text = f"""
📊 **বট স্ট্যাটাস**

✅ **লিমিট বাইপাস API:** {len(LIMIT_BYPASS_APIS)} টি
✅ **User Agents:** {len(USER_AGENTS)} টি
✅ **অফিসিয়াল APIs:** {len(TIKTOK_OFFICIAL_APIS)} টি
✅ **বট স্ট্যাটাস:** চালু ✅
🔄 **আপটাইম:** {int(time.time() - start_time)} সেকেন্ড

🔧 **সিস্টেম লিমিট বাইপাস সক্রিয়!**
        """
        bot.reply_to(message, status_text, parse_mode="Markdown")
    except Exception as e:
        print(f"Status error: {e}")

def extract_video_id(url):
    """URL থেকে TikTok ভিডিও আইডি এক্সট্র্যাক্ট করে"""
    try:
        # বিভিন্ন ফরম্যাটের URL থেকে আইডি এক্সট্র্যাক্ট
        if "/video/" in url:
            parts = url.split("/video/")
            if len(parts) > 1:
                video_id = parts[1].split("?")[0]
                return video_id
        elif "tiktok.com/@" in url:
            # ইউজারনেম সহ URL
            parts = url.split("/")
            for i, part in enumerate(parts):
                if "video" in part and i+1 < len(parts):
                    return parts[i+1].split("?")[0]
        return None
    except:
        return None

def try_tiktok_official_api(video_id):
    """TikTok অফিসিয়াল API ব্যবহার করে ডেটা ফেচ করে"""
    if not video_id:
        return None
    
    for api_url in TIKTOK_OFFICIAL_APIS:
        try:
            headers = {
                "User-Agent": get_random_user_agent(),
                "Accept": "*/*",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate",
                "Referer": "https://www.tiktok.com/",
                "Origin": "https://www.tiktok.com",
                "Connection": "keep-alive",
                "TE": "Trailers",
            }
            
            params = {
                "aweme_id": video_id,
                "iid": "7318518857994389254",
                "device_id": "7318517321748022790",
                "channel": "googleplay",
                "version_code": "300904",
                "device_platform": "android",
                "os_version": "13",
            }
            
            response = requests.get(api_url, headers=headers, params=params, timeout=15)
            if response.status_code == 200:
                data = response.json()
                if "aweme_list" in data and len(data["aweme_list"]) > 0:
                    aweme = data["aweme_list"][0]
                    
                    # ভিডিও ডেটা এক্সট্র্যাক্ট - সম্পূর্ণ তথ্য সহ
                    result = {
                        "code": 0,
                        "data": {
                            "title": aweme.get("desc", "TikTok Video"),
                            "play": None,
                            "hdplay": None,
                            "music": aweme.get("music", {}).get("play_url", {}).get("url_list", [""])[0],
                            "images": [],
                            "author": aweme.get("author", {}),
                            "statistics": aweme.get("statistics", {}),
                            "create_time": aweme.get("create_time", 0)
                        }
                    }
                    
                    # ভিডিও URL পাওয়া
                    video_info = aweme.get("video", {})
                    play_addr = video_info.get("play_addr", {})
                    if play_addr:
                        url_list = play_addr.get("url_list", [])
                        if url_list:
                            result["data"]["play"] = url_list[0]
                    
                    # HD ভিডিও URL
                    download_addr = video_info.get("download_addr", {})
                    if download_addr:
                        url_list = download_addr.get("url_list", [])
                        if url_list:
                            result["data"]["hdplay"] = url_list[0]
                    
                    # ভিডিও ডিটেইলস
                    if video_info:
                        result["data"]["duration"] = video_info.get("duration", 0)
                        result["data"]["ratio"] = video_info.get("ratio", "9:16")
                        result["data"]["cover"] = video_info.get("cover", {}).get("url_list", [""])[0]
                    
                    return result
        except Exception as e:
            print(f"Official API error ({api_url}): {e}")
            continue
    
    return None

def format_caption(video_data, api_name="TikTok API"):
    """ভিডিওর জন্য সম্পূর্ণ ক্যাপশন তৈরি করে"""
    try:
        title = video_data.get("title", "TikTok Video")
        author = video_data.get("author", {})
        stats = video_data.get("statistics", {})
        duration = video_data.get("duration", 0)
        cover = video_data.get("cover", "")
        
        # অথর তথ্য
        author_nickname = author.get("nickname", "Unknown")
        author_username = author.get("unique_id", "")
        
        # স্ট্যাটিস্টিক্স
        views = stats.get("play_count", 0)
        likes = stats.get("digg_count", 0)
        comments = stats.get("comment_count", 0)
        shares = stats.get("share_count", 0)
        downloads = stats.get("download_count", 0)
        
        # সংখ্যা ফরম্যাট করা
        def format_number(num):
            if num >= 1000000:
                return f"{num/1000000:.1f}M"
            elif num >= 1000:
                return f"{num/1000:.1f}K"
            return str(num)
        
        # ক্যাপশন তৈরি
        caption = f"🎬 **TikTok Video**\n\n"
        
        if title and title != "TikTok Video":
            caption += f"📝 **Caption:** {title}\n\n"
        
        if author_nickname:
            caption += f"👤 **Creator:** {author_nickname}"
            if author_username:
                caption += f" (@{author_username})"
            caption += "\n"
        
        if duration > 0:
            minutes = duration // 60
            seconds = duration % 60
            caption += f"⏱️ **Duration:** {minutes}:{seconds:02d}\n"
        
        # স্ট্যাটিস্টিক্স
        stats_text = "📊 **Statistics:**\n"
        if views > 0:
            stats_text += f"  👁️ Views: {format_number(views)}\n"
        if likes > 0:
            stats_text += f"  ❤️ Likes: {format_number(likes)}\n"
        if comments > 0:
            stats_text += f"  💬 Comments: {format_number(comments)}\n"
        if shares > 0:
            stats_text += f"  🔄 Shares: {format_number(shares)}\n"
        if downloads > 0:
            stats_text += f"  ⬇️ Downloads: {format_number(downloads)}\n"
        
        caption += f"\n{stats_text}\n"
        
        # API তথ্য
        caption += f"🔧 **Source:** {api_name}\n"
        caption += f"✅ **Limit Bypass:** Successful\n"
        
        return caption
    
    except Exception as e:
        print(f"Caption formatting error: {e}")
        return f"🎬 TikTok Video\n\n✅ Downloaded Successfully\n🔧 Limit Bypass Active"

def try_multiple_apis(tiktok_url):
    """মাল্টিপল API ব্যবহার করে লিমিট বাইপাস করে"""
    all_results = []
    api_names = []
    
    # প্রথমে অফিসিয়াল API চেষ্টা
    video_id = extract_video_id(tiktok_url)
    if video_id:
        official_result = try_tiktok_official_api(video_id)
        if official_result:
            all_results.append(official_result)
            api_names.append("Official TikTok API")
            print(f"✅ Official API Success")
    
    # তারপর সব লিমিট বাইপাস API চেষ্টা
    for api_info in LIMIT_BYPASS_APIS:
        try:
            api_name = api_info["name"]
            api_url = api_info["url"]
            method = api_info["method"]
            
            print(f"Trying API: {api_name}")
            
            headers = get_headers()
            
            if method == "POST":
                if "ssstik" in api_url:
                    data = {"id": tiktok_url, "locale": "en", "tt": "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=10))}
                elif "musicallydown" in api_url:
                    data = {"query": tiktok_url}
                else:
                    data = {"url": tiktok_url}
                
                response = requests.post(api_url, data=data, headers=headers, timeout=20)
            else:
                params = {"url": tiktok_url}
                response = requests.get(api_url, params=params, headers=headers, timeout=20)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if data:
                        all_results.append(data)
                        api_names.append(api_name)
                        print(f"✅ API Success: {api_name}")
                        
                        # যদি সফল হয়, তাহলে ব্রেক করুন
                        if "code" in data and data["code"] == 0:
                            return data, api_name
                except:
                    continue
        
        except Exception as e:
            print(f"❌ API Failed ({api_info['name']}): {str(e)[:100]}")
            continue
    
    # সবচেয়ে ভালো রেজাল্ট রিটার্ন করুন
    for i, result in enumerate(all_results):
        if "code" in result and result["code"] == 0:
            return result, api_names[i] if i < len(api_names) else "TikTok API"
    
    # যদি কোনোটাই না মেলে, প্রথম valid রেজাল্ট রিটার্ন করুন
    if all_results:
        return all_results[0], api_names[0] if api_names else "TikTok API"
    
    return None, "Unknown"

@bot.message_handler(func=lambda message: True)
def handle_tiktok_url(message):
    """মেইন TikTok ডাউনলোড হ্যান্ডলার"""
    try:
        url = message.text.strip()
        
        # লিংক ভ্যালিডেশন
        if not any(domain in url for domain in ['tiktok.com', 'vt.tiktok.com', 'vm.tiktok.com']):
            bot.reply_to(message, "❌ **ভুল লিংক!** সঠিক TikTok লিংক দিন।", parse_mode="Markdown")
            return
        
        # স্ট্যাটাস মেসেজ
        status_msg = bot.reply_to(message, "🔄 **লিমিট বাইপাস সক্রিয়...**\n\n⚡ লোডিং...", parse_mode="Markdown")
        bot.send_chat_action(message.chat.id, 'upload_video')
        
        # API থেকে ডেটা ফেচ
        data, api_source = try_multiple_apis(url)
        
        if not data:
            bot.edit_message_text(
                "❌ **লিমিট বাইপাস ব্যর্থ!**\n\nট্রাই আবার বা অন্য লিংক দিন।",
                chat_id=message.chat.id,
                message_id=status_msg.message_id,
                parse_mode="Markdown"
            )
            return
        
        # ডেটা প্রসেসিং
        if data.get("code") == 0:
            video_data = data.get("data", {})
            
            # ভিডিও ইনফো
            title = video_data.get("title", "TikTok Video")
            images = video_data.get("images", [])
            video_url = video_data.get("play", "")
            hd_video_url = video_data.get("hdplay", video_url)
            music_url = video_data.get("music", "")
            
            # সম্পূর্ণ ক্যাপশন তৈরি
            full_caption = format_caption(video_data, api_source)
            
            # ফাইনাল ভিডিও URL (HD প্রায়োরিটি)
            final_url = hd_video_url if hd_video_url else video_url
            
            if images and len(images) > 0:
                # স্লাইডশো ভিডিও
                bot.edit_message_text(
                    "📸 **ছবি স্লাইডশো প্রসেসিং...**",
                    chat_id=message.chat.id,
                    message_id=status_msg.message_id,
                    parse_mode="Markdown"
                )
                
                try:
                    # ছবিগুলো পাঠানো
                    media_group = []
                    for img_url in images[:10]:  # সর্বোচ্চ 10টি ছবি
                        media_group.append(InputMediaPhoto(img_url, caption=full_caption if len(media_group) == 0 else None))
                    
                    bot.send_media_group(message.chat.id, media_group)
                    
                    # মিউজিক
                    if music_url:
                        bot.send_audio(message.chat.id, music_url, caption="🎵 TikTok Music")
                    
                    bot.delete_message(message.chat.id, status_msg.message_id)
                    
                except Exception as e:
                    print(f"Image error: {e}")
                    bot.edit_message_text(
                        f"✅ **স্লাইডশো ডাউনলোডেড!**\n\n{full_caption}",
                        chat_id=message.chat.id,
                        message_id=status_msg.message_id,
                        parse_mode="Markdown"
                    )
            
            elif final_url:
                # ভিডিও ডাউনলোড
                bot.edit_message_text(
                    "🚀 **লিমিট ছাড়া ভিডিও প্রসেসিং...**\n\n⚡ HD ভিডিও আপলোড হচ্ছে...",
                    chat_id=message.chat.id,
                    message_id=status_msg.message_id,
                    parse_mode="Markdown"
                )
                
                try:
                    # ভিডিও পাঠানো - সম্পূর্ণ ক্যাপশন সহ
                    bot.send_video(
                        chat_id=message.chat.id,
                        video=final_url,
                        caption=full_caption,
                        parse_mode="Markdown",
                        timeout=300,
                        supports_streaming=True
                    )
                    
                    # অডিও আলাদা
                    if music_url:
                        bot.send_audio(
                            chat_id=message.chat.id,
                            audio=music_url,
                            caption="🎵 TikTok Music",
                            timeout=60
                        )
                    
                    bot.delete_message(message.chat.id, status_msg.message_id)
                    
                except Exception as e:
                    print(f"Video send error: {e}")
                    
                    # বিকল্প পদ্ধতি - লিংক পাঠানো
                    bot.edit_message_text(
                        f"🎬 **TikTok Video**\n\n{full_caption}\n\n"
                        f"🔗 **HD Video Link:** [Download Here]({final_url})\n"
                        f"🔗 **Music Link:** [Download Here]({music_url})" if music_url else "",
                        chat_id=message.chat.id,
                        message_id=status_msg.message_id,
                        parse_mode="Markdown",
                        disable_web_page_preview=True
                    )
            
            else:
                bot.edit_message_text(
                    "❌ **ভিডিও লিংক পাওয়া যায়নি!**\n\n" + full_caption,
                    chat_id=message.chat.id,
                    message_id=status_msg.message_id,
                    parse_mode="Markdown"
                )
        
        else:
            # API এরর
            error_msg = data.get("msg", "Unknown error")
            bot.edit_message_text(
                f"❌ **API Error:** {error_msg}\n\n🔄 লিমিট বাইপাস ট্রাই করছি...",
                chat_id=message.chat.id,
                message_id=status_msg.message_id,
                parse_mode="Markdown"
            )
    
    except Exception as e:
        print(f"Main handler error: {e}")
        try:
            bot.reply_to(message, f"❌ **System Error:** {str(e)[:200]}")
        except:
            pass

# Global start time
start_time = time.time()

def run_bot():
    """বট রান করা"""
    while True:
        try:
            print("🤖 লিমিট বাইপাস বট শুরু হচ্ছে...")
            bot.polling(none_stop=True, interval=0, timeout=60)
        except Exception as e:
            print(f"❌ Polling error: {e}")
            time.sleep(10)

if __name__ == "__main__":
    print(f"""
    ╔══════════════════════════════════════╗
    ║    🚀 TikTok Limit Bypass Bot       ║
    ║    🔥 {len(LIMIT_BYPASS_APIS)} Bypass APIs Active     ║
    ║    ⚡ {len(USER_AGENTS)} User Agents Rotating       ║
    ║    📝 Full Caption + Stats Enabled  ║
    ╚══════════════════════════════════════╝
    """)
    
    # Keep alive ট্রেড শুরু
    Thread(target=keep_alive, daemon=True).start()
    
    # বট শুরু
    run_bot()
