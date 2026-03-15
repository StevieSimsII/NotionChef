import argparse
import os
import sys
import requests
from dotenv import load_dotenv
from recipe_scrapers import scrape_html
from notion_client import Client

load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")


def parse_time(minutes):
    if not minutes:
        return None
    if minutes < 60:
        return f"{minutes} min"
    hours = minutes // 60
    mins = minutes % 60
    return f"{hours}h {mins}min" if mins else f"{hours}h"


def scrape_recipe(url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36"}
    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()
    scraper = scrape_html(response.text, org_url=url, wild_mode=True)
    raw_instructions = scraper.instructions_list()
    if not raw_instructions:
        # Fall back to splitting the single instructions string
        raw = scraper.instructions()
        raw_instructions = [s.strip() for s in raw.split("\n") if s.strip()] if raw else []

    def safe(fn, default=None):
        try:
            return fn()
        except Exception:
            return default

    return {
        "title": safe(scraper.title) or "Untitled Recipe",
        "url": url,
        "servings": safe(scraper.yields),
        "prep_time": parse_time(safe(scraper.prep_time)),
        "cook_time": parse_time(safe(scraper.cook_time)),
        "total_time": parse_time(safe(scraper.total_time)),
        "ingredients": safe(scraper.ingredients, []),
        "instructions": raw_instructions,
        "tags": safe(lambda: scraper.tags(), []),
    }


def rich_text(content):
    # Notion rich_text blocks have a 2000 char limit per item
    chunks = [content[i:i+2000] for i in range(0, len(content), 2000)]
    return [{"type": "text", "text": {"content": chunk}} for chunk in chunks]


def build_blocks(recipe, notes=None):
    blocks = []

    # Metadata section
    meta_lines = []
    if recipe["servings"]:
        meta_lines.append(f"Servings: {recipe['servings']}")
    if recipe["prep_time"]:
        meta_lines.append(f"Prep Time: {recipe['prep_time']}")
    if recipe["cook_time"]:
        meta_lines.append(f"Cook Time: {recipe['cook_time']}")
    if recipe["total_time"]:
        meta_lines.append(f"Total Time: {recipe['total_time']}")
    if recipe["tags"]:
        meta_lines.append(f"Tags: {', '.join(recipe['tags'])}")

    # Source as a hyperlink
    if recipe["url"]:
        blocks.append({
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [
                    {"type": "text", "text": {"content": "Source: "}},
                    {"type": "text", "text": {"content": recipe["url"], "link": {"url": recipe["url"]}}},
                ]
            },
        })

    for line in meta_lines:
        blocks.append({
            "object": "block",
            "type": "paragraph",
            "paragraph": {"rich_text": rich_text(line)},
        })

    blocks.append({"object": "block", "type": "divider", "divider": {}})

    # Ingredients
    blocks.append({
        "object": "block",
        "type": "heading_2",
        "heading_2": {"rich_text": rich_text("Ingredients")},
    })
    for ingredient in recipe["ingredients"]:
        blocks.append({
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": rich_text(ingredient)},
        })

    # Instructions
    blocks.append({
        "object": "block",
        "type": "heading_2",
        "heading_2": {"rich_text": rich_text("Instructions")},
    })
    for step in recipe["instructions"]:
        blocks.append({
            "object": "block",
            "type": "numbered_list_item",
            "numbered_list_item": {"rich_text": rich_text(step)},
        })

    # Notes
    if notes:
        blocks.append({
            "object": "block",
            "type": "heading_2",
            "heading_2": {"rich_text": rich_text("Notes")},
        })
        blocks.append({
            "object": "block",
            "type": "paragraph",
            "paragraph": {"rich_text": rich_text(notes)},
        })

    return blocks


def push_to_notion(recipe, notes=None):
    client = Client(auth=NOTION_TOKEN)

    blocks = build_blocks(recipe, notes=notes)

    page = client.pages.create(
        parent={"database_id": DATABASE_ID},
        properties={
            "Name": {"title": [{"text": {"content": recipe["title"]}}]},
        },
        children=blocks[:100],
    )

    if len(blocks) > 100:
        for i in range(100, len(blocks), 100):
            client.blocks.children.append(
                block_id=page["id"],
                children=blocks[i:i+100],
            )

    return page["url"]


def main():
    parser = argparse.ArgumentParser(description="Save a recipe URL to Notion.")
    parser.add_argument("url", help="The recipe URL to scrape")
    parser.add_argument("--notes", help="Optional notes to append to the recipe", default=None)
    args = parser.parse_args()

    if not NOTION_TOKEN:
        sys.exit("Error: NOTION_TOKEN not set. Add it to your .env file.")
    if not DATABASE_ID:
        sys.exit("Error: NOTION_DATABASE_ID not set. Run `python setup_notion.py` first.")

    print(f"Scraping {args.url} ...")
    recipe = scrape_recipe(args.url)
    print(f"Found: {recipe['title']}")

    print("Pushing to Notion ...")
    notion_url = push_to_notion(recipe, notes=args.notes)
    print(f"Done! View it here: {notion_url}")


if __name__ == "__main__":
    main()
