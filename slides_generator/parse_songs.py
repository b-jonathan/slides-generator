import re
from typing import Dict, List
import uuid


def extract_song_titles(snippet: str) -> list[str]:
    titles = []
    for line in snippet.splitlines():
        if " - " in line:
            # Take text before the dash
            title = line.split(" - ", 1)[0].strip()
            # Remove leading numbers like "1. " or "2) "
            title = re.sub(r"^\s*\d+[\.\)]\s*", "", title)
            if title:
                titles.append(title)
    return titles


def build_title_to_id_map(drive_results: List[Dict]) -> Dict[str, str]:
    return {
        entry["Title"].strip().lower(): entry["Presentation ID"]
        for entry in drive_results
    }


def match_titles_to_ids(titles: List[str], drive_results: List[Dict]) -> List[Dict]:
    title_to_id = build_title_to_id_map(drive_results)
    matches = []
    for t in titles:
        key = t.strip().lower()
        pres_id = title_to_id.get(key)
        matches.append({"title": t, "id": pres_id if pres_id else None})
    return matches


def build_merge_payload(
    titles: List[str],
    drive_results: List[Dict],
    dest_presentation: Dict,
    copy_all: bool = True,
) -> Dict:
    """
    Build the payload for the Apps Script merge endpoint.

    Args:
        titles: list of song titles from songs.txt
        drive_results: list of {Title, Presentation ID} from Drive
        dest_presentation: dict from create_presentation (must include "id")
        copy_all: if True, copy all slides from each matched deck

    Returns:
        dict payload ready to POST
    """
    # Title -> ID map
    title_to_id = {
        entry["Title"].strip().lower(): entry["Presentation ID"]
        for entry in drive_results
    }

    # Build picks
    picks = []
    for t in titles:
        pres_id = title_to_id.get(t.strip().lower())
        if pres_id:
            pick = {"srcId": pres_id}
            if not copy_all:
                pick["slideIndexes"] = "all"  # or pick specific indexes later
            picks.append(pick)

    return {
        "destId": dest_presentation["id"],
        "title": dest_presentation["title"],
        "picks": picks,
        "idempotencyKey": str(uuid.uuid4()),
    }
