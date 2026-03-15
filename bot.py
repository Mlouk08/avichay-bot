import asyncio
import os
from telegram.ext import Application, MessageHandler, filters

SOURCE_CHANNEL     = "@test08102001"  # replace with his channel
TARGET_CHANNEL     = "@lebanese_tehdidet"
TELEGRAM_BOT_TOKEN = "8764676407:AAHwSPSO0hZ1nSERDIbm-w6WYl6N2qa1VdM"

# Keywords to watch for (English, Arabic, Hebrew)
KEYWORDS = [
    "hezbollah",
    "حزب الله",
    "חיזבאללה",
    "hizballah",
    "hizb",
]

def contains_keyword(text):
    if not text:
        return False
    text_lower = text.lower()
    return any(keyword.lower() in text_lower for keyword in KEYWORDS)

async def forward(update, context):
    post = update.channel_post
    if not post:
        return

    text = post.text or post.caption or ""

    if contains_keyword(text):
        await context.bot.forward_message(
            chat_id=TARGET_CHANNEL,
            from_chat_id=post.chat_id,
            message_id=post.message_id
        )
        print(f"✅ Forwarded: {text[:60]}")
    else:
        print(f"⏭️ Skipped: {text[:60]}")

def main():
    print("🤖 Bot started. Filtering for Hezbollah mentions...")
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.ALL, forward))
    app.run_polling()

if __name__ == "__main__":
    main()
