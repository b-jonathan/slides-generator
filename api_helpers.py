"""
List Google Slides in a Drive folder.

Setup
1) pip install google-auth-oauthlib google-api-python-client tabulate
2) In Google Cloud Console, enable the Drive API for your project.
3) Download OAuth client credentials as credentials.json and place next to this script.
4) First run will open a browser to authorize. Token is cached in token.json.

Usage
python read_drive.py "https://drive.google.com/drive/folders/<FOLDER_ID>"
python read_drive.py <FOLDER_ID>
python read_drive.py <FOLDER_ID> --recursive
"""

import datetime
import os
import re
from typing import Dict, List

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/presentations",
]
MIME_SLIDES = "application/vnd.google-apps.presentation"
MIME_FOLDER = "application/vnd.google-apps.folder"


def get_service(api: str = "drive", version: str = "v3"):
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=2500, open_browser=True)
        with open("token.json", "w") as f:
            f.write(creds.to_json())

    return build(api, version, credentials=creds)


def extract_folder_id(s: str) -> str:
    m = re.search(r"/folders/([a-zA-Z0-9_-]+)", s)
    return m.group(1) if m else s.strip()


def list_slides_in_folder(
    service, folder_id: str, recursive: bool = True
) -> List[Dict]:
    results = []

    def query_files(q: str, fields: str, page_size: int = 1000):
        page_token = None
        while True:
            resp = (
                service.files()
                .list(
                    q=q,
                    spaces="drive",
                    fields=f"nextPageToken, files({fields})",
                    pageToken=page_token,
                    pageSize=page_size,
                    includeItemsFromAllDrives=True,
                    supportsAllDrives=True,
                    corpora="user",
                )
                .execute()
            )
            for f in resp.get("files", []):
                yield f
            page_token = resp.get("nextPageToken")
            if not page_token:
                break

    def walk(fid: str):
        slides_q = (
            f"'{fid}' in parents and mimeType = '{MIME_SLIDES}' and trashed = false"
        )
        fields = "id, name"
        for f in query_files(slides_q, fields):
            results.append({
                "Title": f.get("name"),
                "Presentation ID": f.get("id"),
            })
        if recursive:
            folder_q = (
                f"'{fid}' in parents and mimeType = '{MIME_FOLDER}' and trashed = false"
            )
            for sub in query_files(folder_q, "id, name"):
                walk(sub["id"])

    walk(folder_id)
    return results


def create_presentation(slides_service) -> Dict:
    """Create a new Google Slides presentation with the closest Sunday AFTER
    today's date in the title and return metadata + URL.
    """
    today = datetime.date.today()
    # Python's weekday(): Monday == 0 ... Sunday == 6
    weekday = today.weekday()
    # Days until next Sunday strictly after today
    days_ahead = (6 - weekday + 7) % 7
    if days_ahead == 0:
        days_ahead = 7
    next_sunday = today + datetime.timedelta(days=days_ahead)
    body = {"title": next_sunday.strftime("%m/%d/%Y")}
    pres = slides_service.presentations().create(body=body).execute()

    pres_id = pres["presentationId"]
    pres_url = f"https://docs.google.com/presentation/d/{pres_id}/edit"

    return {
        "id": pres_id,
        "title": pres.get("title"),
        "url": pres_url,
    }
