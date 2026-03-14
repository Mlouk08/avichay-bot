
import asyncio
import feedparser
from telegram import Bot

# ============================================================
TELEGRAM_BOT_TOKEN  = "8764676407:AAHwSPSO0hZ1nSERDIbm-w6WYl6N2qa1VdM"
TELEGRAM_CHANNEL    = "@lebanese_tehdidet"
TARGET_USERNAME     = "ALJADEEDNEWS"
CHECK_EVERY_SECONDS = 60
NITTER_RSS = f"https://nitter.tiekoetter.com/{TARGET_USERNAME}/rss"
# ============================================================

tg_bot = Bot(token=TELEGRAM_BOT_TOKEN)

async def run():
    print(f"🤖 Bot started. Watching @{TARGET_USERNAME} every {CHECK_EVERY_SECONDS}s...")
    seen_ids = set()

    # Seed with current posts so we don't resend old ones
    feed = feedparser.entries if hasattr(feedparser, 'entries') else []
    feed = feedparser.parse(NITTER_RSS)
    for entry in feed.entries:
        seen_ids.add(entry.id)
    print(f"📌 Seeded with {len(seen_ids)} existing tweets")

    while True:
        await asyncio.sleep(CHECK_EVERY_SECONDS)
        try:
            feed = feedparser.parse(NITTER_RSS)
            for entry in reversed(feed.entries):
                if entry.id not in seen_ids:
                    seen_ids.add(entry.id)
                    url = entry.link.replace("nitter.poast.org", "x.com")
                    msg = f"🚨 *Warning from Avikhay*\n\n{entry.title}\n\n[View post]({url})"
                    await tg_bot.send_message(chat_id=TELEGRAM_CHANNEL, text=msg, parse_mode="Markdown")
                    print(f"✅ Sent: {entry.title[:60]}")
        except Exception as e:
            print(f"⚠️  Error: {e}")

if __name__ == "__main__":
    asyncio.run(run())
