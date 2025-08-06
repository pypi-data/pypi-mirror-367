import os
import json
from pathlib import Path
from notion_client import Client
from dotenv import load_dotenv

# ---- CONFIG ----
PAGE_ID = "20aa1865-b187-8054-a9bc-c21609f1c6c5"
ENV_PATH = Path.home() / ".incept" / ".env"
OUTPUT_DIR = Path.home() / "Desktop" / "notion_block_export"
ALL_BLOCKS_JSON = OUTPUT_DIR / "all_blocks.json"
BLOCKS_CHUNKS_JSON = OUTPUT_DIR / "blocks_chunks.json"

# ---- LOAD ENV ----
load_dotenv(dotenv_path=ENV_PATH)
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
assert NOTION_API_KEY, "NOTION_API_KEY not found in your .env file!"

# ---- INIT NOTION CLIENT ----
notion = Client(auth=NOTION_API_KEY)

# ---- FETCH BLOCKS ----
def fetch_all_blocks(page_id):
    all_blocks = []
    chunks = []

    next_cursor = None
    chunk_num = 1

    while True:
        response = notion.blocks.children.list(
            block_id=page_id,
            start_cursor=next_cursor,
            page_size=100  # Max page size for Notion API
        )
        print(f"Fetched chunk {chunk_num}: {len(response['results'])} blocks")
        chunks.append(response)
        all_blocks.extend(response["results"])

        if response.get("has_more"):
            next_cursor = response["next_cursor"]
            chunk_num += 1
        else:
            break

    return all_blocks, chunks

# ---- MAIN ----
def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Output will be saved in: {OUTPUT_DIR}")

    all_blocks, chunks = fetch_all_blocks(PAGE_ID)

    # Save all blocks (flat list)
    with open(ALL_BLOCKS_JSON, "w", encoding="utf-8") as f:
        json.dump(all_blocks, f, ensure_ascii=False, indent=2)
    print(f"Saved all {len(all_blocks)} blocks to {ALL_BLOCKS_JSON}")

    # Save chunks (each response from API as separate list item)
    with open(BLOCKS_CHUNKS_JSON, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(chunks)} paginated responses to {BLOCKS_CHUNKS_JSON}")

if __name__ == "__main__":
    main()
