"""
Setup script for Recipe to Notion.

Create a new Recipes database under a page:
    python setup_notion.py --create <parent_page_url>

List accessible databases:
    python setup_notion.py --list

Use an existing database:
    python setup_notion.py --use <database_url_or_id>
"""
import argparse
import os
import re
import sys
from dotenv import load_dotenv
from notion_client import Client

load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")


def extract_id(url_or_id):
    match = re.search(r"([a-f0-9]{32})", url_or_id.replace("-", ""))
    if match:
        raw = match.group(1)
        return f"{raw[:8]}-{raw[8:12]}-{raw[12:16]}-{raw[16:20]}-{raw[20:]}"
    sys.exit("Could not parse a Notion ID from the input.")


def list_databases():
    client = Client(auth=NOTION_TOKEN)
    results = client.search()
    databases = [r for r in results.get("results", []) if r["object"] == "database"]
    if not databases:
        print("No databases found. Make sure your integration is connected to the right pages.")
        return
    print(f"\nFound {len(databases)} database(s) your integration can access:\n")
    for db in databases:
        title = db["title"][0]["plain_text"] if db["title"] else "(untitled)"
        db_id = db["id"]
        print(f"  {title}")
        print(f"    ID: {db_id}")
        print()
    print("Run with --use <ID> to select one.")


def save_database_id(db_id):
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            lines = f.readlines()
        lines = [l for l in lines if not l.startswith("NOTION_DATABASE_ID=")]
    else:
        lines = []
    lines.append(f"NOTION_DATABASE_ID={db_id}\n")
    with open(env_path, "w") as f:
        f.writelines(lines)


def create_database(parent_id):
    client = Client(auth=NOTION_TOKEN)
    db = client.databases.create(
        parent={"type": "page_id", "page_id": parent_id},
        title=[{"type": "text", "text": {"content": "Recipes"}}],
        properties={
            "Name":       {"title": {}},
            "URL":        {"url": {}},
            "Servings":   {"rich_text": {}},
            "Prep Time":  {"rich_text": {}},
            "Cook Time":  {"rich_text": {}},
            "Total Time": {"rich_text": {}},
            "Tags":       {"multi_select": {}},
        },
    )
    return db["id"], db["url"]


def check_database():
    db_id = os.getenv("NOTION_DATABASE_ID")
    if not db_id:
        sys.exit("NOTION_DATABASE_ID not set in .env")
    client = Client(auth=NOTION_TOKEN)
    db = client.databases.retrieve(database_id=db_id)
    title = db["title"][0]["plain_text"] if db["title"] else "(untitled)"
    print(f"\nObject type: {db.get('object')}")
    print(f"Database: {title} ({db_id})")
    print(f"Keys in response: {list(db.keys())}")
    props = db.get("properties", {})
    print(f"Properties ({len(props)}):")
    for name, prop in props.items():
        print(f"  - {name} ({prop['type']})")


def main():
    parser = argparse.ArgumentParser(description="Configure which Notion database to save recipes to.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--create", metavar="PARENT_PAGE_URL", help="Create a new Recipes database under this page")
    group.add_argument("--list", action="store_true", help="List all databases your integration can access")
    group.add_argument("--use", metavar="ID_OR_URL", help="Select an existing database by ID or URL")
    group.add_argument("--check", action="store_true", help="Show properties of the current database in .env")
    args = parser.parse_args()

    if not NOTION_TOKEN:
        sys.exit("Error: NOTION_TOKEN not set. Add it to your .env file first.")

    if args.check:
        check_database()
    elif args.create:
        parent_id = extract_id(args.create)
        print(f"Creating Recipes database ...")
        db_id, db_url = create_database(parent_id)
        save_database_id(db_id)
        print(f"Database created: {db_url}")
        print(f"NOTION_DATABASE_ID saved to .env — you're ready to run recipe.py!")
    elif args.list:
        list_databases()
    elif args.use:
        db_id = extract_id(args.use)
        save_database_id(db_id)
        print(f"NOTION_DATABASE_ID={db_id} saved to .env — you're ready to run recipe.py!")


if __name__ == "__main__":
    main()
