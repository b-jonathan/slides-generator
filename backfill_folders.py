"""One-time script: find 2026 Sunday presentations and move them into {year}/DDM/{MONTH} folders."""

import re
from datetime import datetime

from slides_generator.auth import get_service
from slides_generator.config import DDM_ROOT_FOLDER_ID, SHARE_EMAIL
from slides_generator.drive import (
    move_file_to_folder,
    resolve_folder_path,
    share_file,
)

MIME_SLIDES = "application/vnd.google-apps.presentation"
# Match presentation titles like "01/05/2026", "03/15/2026", etc.
DATE_RE = re.compile(r"^(\d{2})/(\d{2})/(\d{4})$")


def find_date_presentations(drive_service):
    """Search the user's entire Drive for Slides presentations with date titles."""
    results = []
    page_token = None
    q = f"mimeType = '{MIME_SLIDES}' and trashed = false and 'me' in owners"
    while True:
        resp = drive_service.files().list(
            q=q,
            spaces="drive",
            fields="nextPageToken, files(id, name)",
            pageToken=page_token,
            pageSize=1000,
        ).execute()
        for f in resp.get("files", []):
            if DATE_RE.match(f["name"]):
                results.append(f)
        page_token = resp.get("nextPageToken")
        if not page_token:
            break
    return results


def main():
    drive_service = get_service("drive", "v3")

    presentations = find_date_presentations(drive_service)
    print(f"Found {len(presentations)} date-titled presentation(s)\n")

    moved = 0
    for pres in presentations:
        title = pres["name"]
        date = datetime.strptime(title, "%m/%d/%Y")
        if date.year != 2026:
            print(f"  Skipped (not 2026): {title}")
            continue

        pres_id = pres["id"]
        year = str(date.year)
        month = date.strftime("%b").upper()

        print(f"{title} -> {year}/DDM/{month}")

        # Move into folder (creates subfolders if needed)
        target_folder = resolve_folder_path(
            drive_service, DDM_ROOT_FOLDER_ID, [year, "DDM", month]
        )
        move_file_to_folder(drive_service, pres_id, target_folder)

        # Also share with the church email
        try:
            share_file(drive_service, pres_id, SHARE_EMAIL)
        except Exception as e:
            print(f"  Warning: could not share {title}: {e}")

        moved += 1

    print(f"\nDone. Moved {moved} presentation(s).")


if __name__ == "__main__":
    main()
