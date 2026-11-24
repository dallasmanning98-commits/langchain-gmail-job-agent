from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
TRACKER_PATH = Path(os.getenv("TRACKER_PATH", BASE_DIR / "job_search_tracker_UPDATED.xlsx"))
GMAIL_QUERY = os.getenv(
    "GMAIL_QUERY",
    "(job OR jobs OR career OR careers OR hiring OR recruiter OR opportunity OR application OR interview OR position) newer_than:2d",
)
MAX_EMAILS = int(os.getenv("MAX_EMAILS", "25"))
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
