# Update stickers to the stickers.json file
# This should only be called locally 

from typing import Final 
import requests
import json  
import argparse, json, pathlib, sys

# Load from environment variables
TOKEN: Final = "8093326756:AAFdi_Zwk7cGVn1o6Wo43-6DM-RX-2If5YI"
BOT_USERNAME: Final = "@MiniDogStickerBot"
STICKER_SET_NAME = "Mini3554"

TELEGRAM_API = f"https://api.telegram.org/bot{TOKEN}"


# -- BUILDING MAPPING OF EMOJIS/KEYWORDS TO FILE_IDs -- 
url = f"https://api.telegram.org/bot{TOKEN}/getStickerSet?name={STICKER_SET_NAME}"
params = {"name": STICKER_SET_NAME}


# Manually add new emoji and keyword mappings 
response = requests.get(url, params=params)
data = response.json()

emoji_to_file_ids = {}

for sticker in data["result"]["stickers"]:
    emoji = sticker.get("emoji", "").strip()
    file_id = sticker.get("file_id")

    if emoji and file_id:
        emoji_to_file_ids.setdefault(emoji, []).append(file_id)

# Print the result
#print(json.dumps(emoji_to_file_ids, indent=2, ensure_ascii=False))



"""
Take in the corresponding emoji to the sticker and keywords that this sticker can be identified with. 
This code will then map the emoji and keywords to the file_id, updating the stickers.json database. 

Usage: run a python command to add keywords to a new emoji 
  python update_stickers.py \
       --emoji "😎" \
       --keywords "cool" "shades"
"""


DATA_PATH = pathlib.Path(__file__).with_name("stickers.json")

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--emoji", required=True)
    p.add_argument("--keywords", nargs="+", required=True)
    args = p.parse_args()

    # find file_id for the emoji argument
    file_id = emoji_to_file_ids[args.emoji]

    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    # if the emoji already exists, append; else create
    for row in data:
        if row["emoji"] == args.emoji:
            if file_id not in row["file_ids"]:
                row["file_ids"].append(file_id)
            row["keywords"] = sorted(set(row["keywords"]) | set(map(str.lower, args.keywords)))
            break
    else:  # new emoji
        data.append(
            {
                "emoji": args.emoji,
                "file_ids": file_id,
                "keywords": list(map(str.lower, args.keywords)),
            }
        )

    DATA_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    print("✅ stickers.json updated.")

if __name__ == "__main__":
    sys.exit(main())

