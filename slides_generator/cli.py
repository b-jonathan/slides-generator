import argparse
import json
import os
import re

import requests as http_requests

from .auth import get_service
from .config import DDM_ROOT_FOLDER_ID, DRIVE_FOLDER_ID, LYRICS_DIR, SHARE_EMAIL, SONGS_FILE, WEBAPP_URL
from .drive import (
    copy_presentation,
    get_random_background_url,
    list_slides_in_folder,
    move_file_to_folder,
    resolve_folder_path,
    share_file,
)
from .parse_lyrics import parse_and_chunk
from .parse_songs import (
    build_merge_payload,
    extract_song_titles,
    match_titles_to_ids,
)
from .slides import build_lyric_presentation_requests, create_presentation, next_sunday


# ── Shared helpers ──────────────────────────────────────────────

def _read_songs():
    with open(SONGS_FILE) as f:
        return extract_song_titles(f.read())


def _query_drive(drive_service):
    return list_slides_in_folder(drive_service, DRIVE_FOLDER_ID)


# ── Subcommands ─────────────────────────────────────────────────

def cmd_check(args):
    """List which songs from songs.txt are found (or missing) in Drive."""
    drive_service = get_service("drive", "v3")
    titles = _read_songs()
    print("Extracted titles:", titles)

    drive_results = _query_drive(drive_service)
    matches = match_titles_to_ids(titles, drive_results)
    print(json.dumps(matches, indent=2))


def cmd_generate(args):
    """Create individual lyric presentations from lyrics/ files."""
    drive_service = get_service("drive", "v3")
    slides_service = get_service("slides", "v1")

    # Fetch existing presentations in the Drive folder to skip duplicates
    existing_normalized = {
        re.sub(r"[^a-z0-9]", "", item["Title"].lower())
        for item in _query_drive(drive_service)
    }

    for filename in sorted(os.listdir(LYRICS_DIR)):
        if not filename.endswith(".txt"):
            continue
        song_title = filename.removesuffix(".txt").replace("_", " ").title()

        if re.sub(r"[^a-z0-9]", "", song_title.lower()) in existing_normalized:
            print(f"Skipping {song_title}: already exists in Drive")
            continue

        filepath = os.path.join(LYRICS_DIR, filename)

        with open(filepath) as f:
            lines = f.read().splitlines()
        # Skip the first line (title) so it isn't treated as a lyric
        raw = "\n".join(lines[1:])
        chunks = parse_and_chunk(raw)
        if not chunks:
            print(f"Skipping {song_title}: no lyric chunks produced")
            continue

        print(f"\n── {song_title} ({len(chunks)} slides) ──")

        # Pick a random background image
        bg_url = get_random_background_url(drive_service)

        # Create a blank presentation titled with the song name
        pres = create_presentation(slides_service, title=song_title)
        pres_id = pres["id"]
        print(f"  Created: {pres['url']}")

        # Read the default first slide to get its ID + placeholder IDs
        full = slides_service.presentations().get(presentationId=pres_id).execute()
        first_slide = full["slides"][0]
        title_slide_id = first_slide["objectId"]
        placeholder_ids = [
            el["objectId"]
            for el in first_slide.get("pageElements", [])
        ]

        # Build and execute the batch update
        reqs = build_lyric_presentation_requests(
            title_slide_id, chunks, bg_url, song_title, placeholder_ids
        )
        slides_service.presentations().batchUpdate(
            presentationId=pres_id, body={"requests": reqs}
        ).execute()
        print(f"  Populated {len(chunks)} lyric slides")

        # Move into the Drive folder
        move_file_to_folder(drive_service, pres_id, DRIVE_FOLDER_ID)
        print(f"  Moved to folder {DRIVE_FOLDER_ID}")


def cmd_compile(args):
    """Merge existing song decks into one Sunday presentation via Apps Script."""
    drive_service = get_service("drive", "v3")
    titles = _read_songs()
    print("Extracted titles:", titles)

    drive_results = _query_drive(drive_service)
    matches = match_titles_to_ids(titles, drive_results)
    print(json.dumps(matches, indent=2))

    missing = [m["title"] for m in matches if m["id"] is None]
    if missing:
        print(f"\nMissing {len(missing)} song(s) in Drive:")
        for title in missing:
            print(f"  - {title}")
        print("\nAborting. Add the missing songs to Drive and try again.")
        return

    slides_service = get_service("slides", "v1")
    presentation = create_presentation(slides_service)
    payload = build_merge_payload(titles, drive_results, presentation)
    print(payload)

    resp = http_requests.post(WEBAPP_URL, json=payload)
    print(resp.status_code)
    print(resp.text)

    pres_id = presentation["id"]

    # Share with the church email
    share_file(drive_service, pres_id, SHARE_EMAIL)
    print(f"Shared with {SHARE_EMAIL}")

    # Move into {year}/DDM/{month} folder structure
    sunday = next_sunday()
    year = str(sunday.year)
    month = sunday.strftime("%b").upper()  # e.g. "MAR"
    target_folder = resolve_folder_path(
        drive_service, DDM_ROOT_FOLDER_ID, [year, "DDM", month]
    )
    move_file_to_folder(drive_service, pres_id, target_folder)
    print(f"Moved to {year}/DDM/{month}")


# ── Entry point ─────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Slides generator CLI")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("check", help="List found/missing songs in Drive")
    sub.add_parser("generate", help="Create lyric presentations from lyrics/")
    sub.add_parser("compile", help="Merge song decks into one Sunday presentation")

    args = parser.parse_args()

    commands = {
        "check": cmd_check,
        "generate": cmd_generate,
        "compile": cmd_compile,
    }

    if args.command in commands:
        commands[args.command](args)
    else:
        parser.print_help()
