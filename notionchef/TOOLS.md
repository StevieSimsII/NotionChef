# TOOLS.md — Local Setup Notes (NotionChef)

## Required Env Vars
- NOTION_TOKEN
- NOTION_DATABASE_ID
- TELEGRAM_BOT_TOKEN (bot mode only)

## Common Commands
- Check Notion DB:
python setup_notion.py --check

- Create DB:
python setup_notion.py --create <parent_page_url>

- List DBs:
python setup_notion.py --list

- Use existing DB:
python setup_notion.py --use <database_url_or_id>

- Import recipe URL:
python recipe.py "<url>"

- Run Telegram bot:
python bot.py

## Notes
- Keep `.env` local only
- If Notion access fails, verify page/database is shared with integration