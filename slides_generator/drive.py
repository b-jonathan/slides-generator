import random
import re
from typing import Dict, List

from .config import BACKGROUNDS_FOLDER_ID, MIME_FOLDER, MIME_IMAGE, MIME_SLIDES


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
                    corpora="allDrives",
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


def list_images_in_folder(service, folder_id: str) -> List[Dict]:
    """List all image files in a Drive folder."""
    images = []
    page_token = None
    q = f"'{folder_id}' in parents and mimeType contains '{MIME_IMAGE}' and trashed = false"
    while True:
        resp = (
            service.files()
            .list(
                q=q,
                spaces="drive",
                fields="nextPageToken, files(id, name, mimeType)",
                pageToken=page_token,
                pageSize=1000,
                includeItemsFromAllDrives=True,
                supportsAllDrives=True,
                corpora="allDrives",
            )
            .execute()
        )
        images.extend(resp.get("files", []))
        page_token = resp.get("nextPageToken")
        if not page_token:
            break
    return images


def get_random_background_url(service, folder_id: str = BACKGROUNDS_FOLDER_ID) -> str:
    """Pick a random image from a Drive folder and return a URL usable by the Slides API.

    Ensures the image is publicly readable so the Slides API can fetch it server-side.
    """
    images = list_images_in_folder(service, folder_id)
    if not images:
        raise ValueError(f"No images found in folder {folder_id}")
    chosen = random.choice(images)
    file_id = chosen["id"]
    print(f"Selected background: {chosen['name']}")

    # Ensure the file is publicly readable (required for Slides API)
    try:
        service.permissions().create(
            fileId=file_id,
            body={"type": "anyone", "role": "reader"},
            supportsAllDrives=True,
        ).execute()
    except Exception:
        pass  # Permission may already exist

    return f"https://drive.google.com/uc?id={file_id}&export=download"


def copy_presentation(drive_service, source_id: str, title: str) -> Dict:
    """Copy a presentation via the Drive API and return the new file's metadata."""
    copy = (
        drive_service.files()
        .copy(
            fileId=source_id,
            body={"name": title},
            supportsAllDrives=True,
        )
        .execute()
    )
    new_id = copy["id"]
    return {
        "id": new_id,
        "title": title,
        "url": f"https://docs.google.com/presentation/d/{new_id}/edit",
    }


def move_file_to_folder(drive_service, file_id: str, folder_id: str):
    """Move a file into a Drive folder using addParents/removeParents."""
    file = drive_service.files().get(
        fileId=file_id,
        fields="parents",
        supportsAllDrives=True,
    ).execute()
    previous_parents = ",".join(file.get("parents", []))
    drive_service.files().update(
        fileId=file_id,
        addParents=folder_id,
        removeParents=previous_parents,
        supportsAllDrives=True,
    ).execute()


def share_file(drive_service, file_id: str, email: str, role: str = "writer"):
    """Share a file with a specific email address."""
    drive_service.permissions().create(
        fileId=file_id,
        body={"type": "user", "role": role, "emailAddress": email},
        supportsAllDrives=True,
        sendNotificationEmail=False,
    ).execute()


def find_or_create_folder(drive_service, parent_id: str, name: str) -> str:
    """Find a subfolder by name under parent_id, or create it. Returns the folder ID."""
    q = (
        f"'{parent_id}' in parents"
        f" and mimeType = '{MIME_FOLDER}'"
        f" and name = '{name}'"
        f" and trashed = false"
    )
    resp = drive_service.files().list(
        q=q,
        spaces="drive",
        fields="files(id)",
        pageSize=1,
        includeItemsFromAllDrives=True,
        supportsAllDrives=True,
        corpora="allDrives",
    ).execute()
    files = resp.get("files", [])
    if files:
        return files[0]["id"]
    # Create the folder
    metadata = {
        "name": name,
        "mimeType": MIME_FOLDER,
        "parents": [parent_id],
    }
    folder = drive_service.files().create(
        body=metadata,
        fields="id",
        supportsAllDrives=True,
    ).execute()
    return folder["id"]


def resolve_folder_path(drive_service, root_id: str, path_parts: list[str]) -> str:
    """Walk/create a chain of subfolders and return the final folder ID.

    E.g. resolve_folder_path(svc, root, ["DDM", "2026", "March"])
    """
    current = root_id
    for part in path_parts:
        current = find_or_create_folder(drive_service, current, part)
    return current
