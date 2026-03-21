import os

SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/presentations",
]
MIME_SLIDES = "application/vnd.google-apps.presentation"
MIME_FOLDER = "application/vnd.google-apps.folder"
MIME_IMAGE = "image/"

BACKGROUNDS_FOLDER_ID = "1djzBmYcwSgQN-hYcgN4Jf_0QE_QS1TeS"
DRIVE_FOLDER_ID = "1UTwL0O20EsKxlHZfy89S8YF7SYBt73Rz"
DDM_ROOT_FOLDER_ID = "1onOQgtRdprBaemS7nhpjlCQfysOylZh7"
SHARE_EMAIL = "sdcityblessing@gmail.com"

WEBAPP_URL = (
    "https://script.google.com/macros/s/"
    "AKfycbwWsHVETAgUop6CeW5RmM1rSlCvCU0mNjqOqxRz2zDlYcPnkCxwjEJk8Y-K70U1Z1ms/exec"
)

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOKEN_PATH = os.path.join(REPO_ROOT, "token.json")
CREDENTIALS_PATH = os.path.join(REPO_ROOT, "credentials.json")

SONGS_FILE = os.path.join(REPO_ROOT, "songs.txt")
LYRICS_DIR = os.path.join(REPO_ROOT, "lyrics")
