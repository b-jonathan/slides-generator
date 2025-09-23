from api_helpers import create_presentation, get_service


SCOPES = [
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/presentations",
]
MIME_SLIDES = "application/vnd.google-apps.presentation"
MIME_FOLDER = "application/vnd.google-apps.folder"

slides_service = get_service("slides", "v1")
presentation = create_presentation(slides_service)
print("Created:", presentation.get("url"))
