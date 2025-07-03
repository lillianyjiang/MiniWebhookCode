# helpers.py
import json, pathlib
from collections import defaultdict
from typing import Dict, List, Tuple

DATA_PATH = pathlib.Path(__file__).with_name("stickers.json")

def load_mappings() -> Tuple[Dict[str, List[str]], Dict[str, List[str]]]:
    """
    Read stickers.json once and build (emoji_to_file_ids, keyword_to_file_ids).
    """
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))

    emoji_to_files: Dict[str, List[str]] = {
        row["emoji"]: row["file_ids"] for row in data
    }

    keyword_to_files: Dict[str, List[str]] = defaultdict(list)
    for row in data:
        for kw in row["keywords"]:
            keyword_to_files[kw.lower()].extend(row["file_ids"])

    return emoji_to_files, keyword_to_files
