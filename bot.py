import asyncio
import httpx
from telegram import Bot

# ============================================================
TELEGRAM_BOT_TOKEN  = "8764676407:AAHwSPSO0hZ1nSERDIbm-w6WYl6N2qa1VdM"
TELEGRAM_CHANNEL    = "@lebanese_tehdidet"
TARGET_USERNAME     = "AvichayAdraee"
CHECK_EVERY_SECONDS = 300

tg_bot = Bot(token=TELEGRAM_BOT_TOKEN)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/javascript, */*",
    "Referer": "https://x.com",
}

async def get_tweets():
    url = f"https://syndication.twitter.com/srv/timeline-profile/screen-name/{TARGET_USERNAME}?count=20&showReplies=false"
    async with httpx.AsyncClient(headers=HEADERS, timeout=30, follow_redirects=True) as client:
        for attempt in range(3):
            r = await client.get(url)
            print(f"🔍 Status: {r.status_code}")
            if r.status_code == 429:
                print(f"⏳ Rate limited, waiting 60s before retry...")
                await asyncio.sleep(60)
                continue
            data = r.json()
            entries = data.get("timeline", {}).get("entries", [])
            tweets = []
            for entry in entries:
                tweet = entry.get("content", {}).get("tweet", {})
                if tweet:
                    tweets.append({
                        "id": tweet.get("id_str"),
                        "text": tweet.get("full_text", tweet.get("text", "")),
                    })
            return tweets
        return []

async def run():
    print(f"🤖 Bot started. Watching @{TARGET_USERNAME} every {CHECK_EVERY_SECONDS}s...")
    seen_ids = set()

    try:
        tweets = await get_tweets()
        for t in tweets:
            seen_ids.add(t["id"])
        print(f"📌 Seeded with {len(seen_ids)} existing tweets")
    except Exception as e:
        print(f"⚠️ Startup error: {e}")

    while True:
        await asyncio.sleep(CHECK_EVERY_SECONDS)
        try:
            tweets = await get_tweets()
            for tweet in reversed(tweets):
                if tweet["id"] not in seen_ids:
                    seen_ids.add(tweet["id"])
                    url = f"https://x.com/{TARGET_USERNAME}/status/{tweet['id']}"
                    msg = f"🚨 *Warning from Avikhay*\n\n{tweet['text']}\n\n[View post]({url})"
                    await tg_bot.send_message(chat_id=TELEGRAM_CHANNEL, text=msg, parse_mode="Markdown")
                    print(f"✅ Sent: {tweet['text'][:60]}")
        except Exception as e:
            print(f"⚠️ Error: {e}")

if __name__ == "__main__":
    asyncio.run(run())
