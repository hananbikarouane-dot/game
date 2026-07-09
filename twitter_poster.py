import os
import random
import tweepy

# استقبال المفاتيح السرية من بيئة جيت هاب بأمان
API_KEY = os.environ.get("TWITTER_API_KEY")
API_KEY_SECRET = os.environ.get("TWITTER_API_KEY_SECRET")
ACCESS_TOKEN = os.environ.get("TWITTER_ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.environ.get("TWITTER_ACCESS_TOKEN_SECRET")

# 📚 مصفوفة القصص الطويلة الاحترافية لزيادة الـ Retention والتفاعل في أمريكا
RANDOM_STORIES = [
    (
        "The Real-Life 'Limitless' Pill Exists... 🧠💊\n\n"
        "In the famous movie 'Limitless', Eddie Morra takes a secret clear pill called NZT-48, unlocking 100% of his brain capacity. "
        "Instantly, he masters the stock market and builds an empire.\n\n"
        "But in 2026, the real 'clear pill' isn't chemical—it's architecture. While average business owners waste 14 hours a day on manual tasks, "
        "top-tier founders use automated Python scripts to catch leads on autopilot.\n\n"
        "I archived the exact modern automated setup for free today. Access the link in my bio to unlock 100% efficiency! "
        "#automation #solopreneur #aitools #growthhacking"
    ),
    (
        "How Elon Musk's First Million-Dollar Code Was Written 🚀👨‍💻\n\n"
        "Back in 1995, a young Elon Musk slept on a couch in a tiny office, coding Zip2 7 days a week. He realized early on that code "
        "is the ultimate leverage because it works for you when you can't.\n\n"
        "Today, you don't need to sleep on a couch to scale. By using automated Python networks, you can deploy digital traps "
        "that capture leads 24/7 on autopilot.\n\n"
        "Get the full automated business roadmap for free via the link in my bio today! "
        "#elonmusk #buildinpublic #python #marketing"
    ),
    (
        "The Dark Psychology of the 'Baader-Meinhof' Phenomenon 🧐🔥\n\n"
        "Ever notice that when you learn a new rare concept, suddenly you start seeing it EVERYWHERE? "
        "This is a psychological trigger called the Frequency Illusion. Your brain highlights it once it flags it as important.\n\n"
        "Smart businesses use this exact psychological hack to dominate markets. By setting up an automated multichannel digital presence, "
        "you force your brand to appear everywhere your client looks, making you inevitable.\n\n"
        "Want to build this automated omnipresence system? Grab the complete free blueprint via my bio link right now. "
        "#psychology #marketingtips #saas"
    )
]

def post_to_twitter():
    if not all([API_KEY, API_KEY_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET]):
        raise Exception("❌ Error: Twitter API Keys are missing from GitHub Secrets!")

    # الاتصال بالجيل الثاني الحديث لنظام تويتر (v2 API)
    client = tweepy.Client(
        consumer_key=API_KEY,
        consumer_secret=API_KEY_SECRET,
        access_token=ACCESS_TOKEN,
        access_token_secret=ACCESS_TOKEN_SECRET
    )

    # اختيار قصة عشوائية ونشرها
    story = random.choice(RANDOM_STORIES)
    print("🚀 US Server: Preparing to post the story on X...")
    
    response = client.create_tweet(text=story)
    print(f"🎉 Success! Tweet posted successfully. Tweet ID: {response.data['id']}")

if __name__ == "__main__":
    try:
        post_to_twitter()
    except Exception as e:
        print(f"❌ Twitter Automation Error: {e}")
