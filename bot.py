import asyncio
import httpx
import os
from telegram import Bot

TELEGRAM_BOT_TOKEN = "8764676407:AAHwSPSO0hZ1nSERDIbm-w6WYl6N2qa1VdM"
TELEGRAM_CHANNEL    = "@lebanese_tehdidet"
TARGET_USERNAME     = "ALJADEEDNEWS"
CHECK_EVERY_SECONDS = 300

tg_bot = Bot(token=TELEGRAM_BOT_TOKEN)

RSSHUB_INSTANCES = [
    "https://rsshub.app",
    "https://rss.shab.fun",
    "https://rsshub.rssforever.com",
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
}

async def get_tweets():
    for instance in RSSHUB_INSTANCES:
        url = f"{instance}/twitter/user/{TARGET_USERNAME}"
        try:
            async with httpx.AsyncClient(headers=HEADERS, timeout=30, follow_redirects=True) as client:
                r = await client.get(url)
                print(f"🔍 {instance} → Status: {r.status_code}")
                if r.status_code == 200 and "<item>" in r.text:
                    print(f"✅ Got feed from {instance}")
                    return parse_rss(r.text), instance
        except Exception as e:
            print(f"⚠️ {instance} failed: {e}")
    return [], None

def parse_rss(xml):
    import re
    tweets = []
    items = re.findall(r"<item>(.*?)</item>", xml, re.DOTALL)
    for item in items:
        title = re.search(r"<title><!\[CDATA\[(.*?)\]\]></title>", item, re.DOTALL)
        link  = re.search(r"<link>(.*?)</link>", item)
        guid  = re.search(r"<guid>(.*?)</guid>", item)
        if title and link and guid:
            tweets.append({
                "id": guid.group(1),
                "text": title.group(1).strip(),
                "url": link.group(1).strip(),
            })
    return tweets

async def run():
    print(f"🤖 Bot started. Watching @{TARGET_USERNAME} every {CHECK_EVERY_SECONDS}s...")
    seen_ids = set()

    tweets, instance = await get_tweets()
    for t in tweets:
        seen_ids.add(t["id"])
    print(f"📌 Seeded with {len(seen_ids)} existing tweets")

    while True:
        await asyncio.sleep(CHECK_EVERY_SECONDS)
        try:
            tweets, instance = await get_tweets()
            for tweet in reversed(tweets):
                if tweet["id"] not in seen_ids:
                    seen_ids.add(tweet["id"])
                    msg = f"🚨 *Warning from Avikhay*\n\n{tweet['text']}\n\n[View post]({tweet['url']})"
                    await tg_bot.send_message(chat_id=TELEGRAM_CHANNEL, text=msg, parse_mode="Markdown")
                    print(f"✅ Sent: {tweet['text'][:60]}")
        except Exception as e:
            print(f"⚠️ Error: {e}")

if __name__ == "__main__":
    asyncio.run(run())
