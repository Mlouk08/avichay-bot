
import asyncio
import feedparser
from telegram import Bot

# ============================================================
TELEGRAM_BOT_TOKEN  = "8764676407:AAHwSPSO0hZ1nSERDIbm-w6WYl6N2qa1VdM"
TELEGRAM_CHANNEL    = "@lebanese_tehdidet"
TARGET_USERNAME     = "ALJADEEDNEWS"
CHECK_EVERY_SECONDS = 60
NITTER_INSTANCES = [
    "https://nitter.tiekoetter.com",
    "https://nitter.poast.org",
    "https://nitter.privacydev.net",
    "https://nitter.cz",
]
# ============================================================

tg_bot = Bot(token=TELEGRAM_BOT_TOKEN)

def get_feed():
    for instance in NITTER_INSTANCES:
        url = f"{instance}/{TARGET_USERNAME}/rss"
        feed = feedparser.parse(url)
        if feed.entries:
            print(f"✅ Using instance: {instance} ({len(feed.entries)} entries)")
            return feed, instance
        else:
            print(f"⚠️ No entries from {instance}, trying next...")
    return None, None

async def run():
    print(f"🤖 Bot started. Watching @{TARGET_USERNAME} every {CHECK_EVERY_SECONDS}s...")
    seen_ids = set()

    feed, instance = get_feed()
    if feed:
        for entry in feed.entries:
            seen_ids.add(entry.id)
        print(f"📌 Seeded with {len(seen_ids)} existing tweets")
    else:
        print("⚠️ All Nitter instances returned 0 entries at startup")

    while True:
        await asyncio.sleep(CHECK_EVERY_SECONDS)
        try:
            feed, instance = get_feed()
            if not feed:
                print("⚠️ All instances failed this round, will retry next cycle")
                continue
            for entry in reversed(feed.entries):
                if entry.id not in seen_ids:
                    seen_ids.add(entry.id)
                    url = entry.link.replace(instance.replace("https://", ""), "x.com")
                    msg = f"🚨 *Warning from Avikhay*\n\n{entry.title}\n\n[View post]({url})"
                    await tg_bot.send_message(chat_id=TELEGRAM_CHANNEL, text=msg, parse_mode="Markdown")
                    print(f"✅ Sent: {entry.title[:60]}")
        except Exception as e:
            print(f"⚠️ Error: {e}")

if __name__ == "__main__":
    asyncio.run(run())
