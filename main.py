# ===========================
# Config
# ===========================
import json

import requests

from api_helpers import (
    create_presentation,
    extract_folder_id,
    get_service,
    list_slides_in_folder,
)
from parse_songs import build_merge_payload, extract_song_titles, match_titles_to_ids

SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/presentations",
]
MIME_SLIDES = "application/vnd.google-apps.presentation"
MIME_FOLDER = "application/vnd.google-apps.folder"

SONGS_FILE = "songs.txt"
DRIVE_FOLDER_URL = (
    "https://drive.google.com/drive/folders/1UTwL0O20EsKxlHZfy89S8YF7SYBt73Rz"
)


def main():
    # Read songs.txt
    with open(SONGS_FILE, "r", encoding="utf-8") as f:
        snippet = f.read()
    titles = extract_song_titles(snippet)
    print("Extracted titles:", titles)

    # Drive query
    folder_id = extract_folder_id(DRIVE_FOLDER_URL)
    service = get_service()
    drive_results = list_slides_in_folder(service, folder_id)

    # Match
    matches = match_titles_to_ids(titles, drive_results)

    # Print JSON output
    print(json.dumps(matches, indent=2))

    slides_service = get_service("slides", "v1")
    presentation = create_presentation(slides_service)
    payload = build_merge_payload(titles, drive_results, presentation)
    print(payload)

    WEBAPP_URL = "https://script.google.com/macros/s/AKfycbwWsHVETAgUop6CeW5RmM1rSlCvCU0mNjqOqxRz2zDlYcPnkCxwjEJk8Y-K70U1Z1ms/exec"

    resp = requests.post(WEBAPP_URL, json=payload)
    print(resp.status_code)
    print(resp.text)


if __name__ == "__main__":
    main()
