# NotionChef

NotionChef is a small Python project that scrapes recipe pages and saves them into a Notion database.

It supports two ways to use it:

- a command-line workflow for saving a recipe from a URL
- a Telegram bot that accepts recipe links and pushes them to Notion

## What it does

- Scrapes recipe pages with `recipe-scrapers`
- Extracts title, ingredients, instructions, times, servings, and tags when available
- Builds a structured Notion page with recipe content
- Can create or select a Notion database for storing recipes
- Can run as a Telegram bot for quick recipe capture

## Project structure

- `bot.py` — Telegram bot entry point
- `recipe.py` — scraping logic, Notion page creation, and CLI entry point
- `setup_notion.py` — helper script for creating, listing, selecting, and checking a Notion database
- `requirements.txt` — Python dependencies

## Requirements

- Python 3
- A Notion integration token
- A Notion page or database shared with that integration
- A Telegram bot token if using the bot

## Installation

1. Clone or copy this project.
2. Create and activate a virtual environment.
3. Install dependencies:

```bash
pip install -r requirements.txt
```

## Environment variables

Create a `.env` file in the project root.

Example:

```env
NOTION_TOKEN=your_notion_integration_token
NOTION_DATABASE_ID=your_database_id
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
```

Notes:

- `NOTION_TOKEN` is required for all Notion operations.
- `NOTION_DATABASE_ID` is required for saving recipes.
- `TELEGRAM_BOT_TOKEN` is only required for `bot.py`.
- `NOTION_DATABASE_ID` can be added automatically by `setup_notion.py`.

## Notion setup

Before saving recipes, the Notion integration must have access to a page or database.

### Option 1: Create a new Recipes database

Run:

```bash
python setup_notion.py --create <parent_page_url>
```

This will:

- create a `Recipes` database under the given Notion page
- save the new `NOTION_DATABASE_ID` into `.env`

### Option 2: List available databases

Run:

```bash
python setup_notion.py --list
```

### Option 3: Use an existing database

Run:

```bash
python setup_notion.py --use <database_url_or_id>
```

### Option 4: Check current database

Run:

```bash
python setup_notion.py --check
```

## Usage

### Save a recipe from the command line

```bash
python recipe.py "https://example.com/recipe"
```

Optional notes can be appended:

```bash
python recipe.py "https://example.com/recipe" --notes "Family favorite. Reduce salt a little."
```

### Run the Telegram bot

```bash
python bot.py
```

Then send the bot a recipe URL.

The bot will:

1. receive the URL
2. scrape the recipe
3. save it to Notion
4. reply with the Notion page link

## How the data is stored in Notion

Each saved recipe becomes a Notion page with:

- the recipe title as the page name
- a linked source URL
- servings and timing metadata when available
- an ingredients section
- an instructions section
- an optional notes section

## Typical workflow

1. Add `NOTION_TOKEN` to `.env`
2. Create or select a Notion database with `setup_notion.py`
3. Test recipe import with `recipe.py`
4. Add `TELEGRAM_BOT_TOKEN` to `.env`
5. Start `bot.py` for chat-based recipe capture

## Troubleshooting

### `NOTION_TOKEN not set`

Add `NOTION_TOKEN` to the `.env` file.

### `NOTION_DATABASE_ID not set`

Run one of the setup commands in `setup_notion.py` to create or select a database.

### No databases found

Make sure the Notion integration has been shared with the relevant page or database.

### Telegram bot will not start

Make sure `TELEGRAM_BOT_TOKEN` exists in `.env`.

## Security notes

- Do not commit `.env` to source control.
- Keep the Notion token and Telegram bot token private.

## Summary

NotionChef is a lightweight recipe capture tool:

- `setup_notion.py` prepares Notion
- `recipe.py` scrapes and saves recipes
- `bot.py` provides a Telegram interface
