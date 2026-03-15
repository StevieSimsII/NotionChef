import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

from recipe import scrape_recipe, push_to_notion

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_BOT_TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN not found in .env")

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if not text.startswith("http"):
        await update.message.reply_text("Send me a recipe URL and I'll save it to Notion.")
        return

    await update.message.reply_text("Scraping recipe...")

    try:
        recipe = scrape_recipe(text)
    except Exception as e:
        await update.message.reply_text(f"Couldn't scrape that page: {e}")
        return

    await update.message.reply_text(f"Found: {recipe['title']}\nSaving to Notion...")

    try:
        notion_url = push_to_notion(recipe)
    except Exception as e:
        await update.message.reply_text(f"Saved the recipe but couldn't push to Notion: {e}")
        return

    await update.message.reply_text(f"Done! {recipe['title']} saved.\n{notion_url}")


def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("NotionChefBot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
