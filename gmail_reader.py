from __future__ import annotations

import base64
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from config import BASE_DIR, SCOPES


def get_gmail_service():
    """Authenticate with Gmail and return a Gmail API service object."""
    token_path = BASE_DIR / "token.json"
    credentials_path = BASE_DIR / "credentials.json"
    creds = None

    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not credentials_path.exists():
                raise FileNotFoundError(
                    "Missing credentials.json. Download OAuth desktop credentials from Google Cloud and place it in this folder."
                )
            flow = InstalledAppFlow.from_client_secrets_file(str(credentials_path), SCOPES)
            creds = flow.run_local_server(port=0)
        token_path.write_text(creds.to_json(), encoding="utf-8")

    return build("gmail", "v1", credentials=creds)


def _headers_to_dict(headers: list[dict[str, str]]) -> dict[str, str]:
    return {h.get("name", "").lower(): h.get("value", "") for h in headers}


def _decode_part_body(data: str | None) -> str:
    if not data:
        return ""
    return base64.urlsafe_b64decode(data.encode("utf-8")).decode("utf-8", errors="replace")


def _extract_text(payload: dict[str, Any]) -> str:
    """Extract readable text/plain or fallback HTML text from Gmail payload."""
    mime_type = payload.get("mimeType", "")
    body = payload.get("body", {})

    if mime_type == "text/plain":
        return _decode_part_body(body.get("data"))

    if mime_type == "text/html":
        return _decode_part_body(body.get("data"))

    parts = payload.get("parts", []) or []
    chunks = []
    for part in parts:
        text = _extract_text(part)
        if text:
            chunks.append(text)
    return "\n".join(chunks)


def search_job_emails(query: str, max_results: int = 25) -> list[dict[str, Any]]:
    """Search Gmail and return message summaries plus body text."""
    service = get_gmail_service()
    results = service.users().messages().list(userId="me", q=query, maxResults=max_results).execute()
    messages = results.get("messages", [])

    emails = []
    for msg in messages:
        full = service.users().messages().get(userId="me", id=msg["id"], format="full").execute()
        payload = full.get("payload", {})
        headers = _headers_to_dict(payload.get("headers", []))
        date_raw = headers.get("date", "")
        try:
            email_date = parsedate_to_datetime(date_raw).isoformat()
        except Exception:
            email_date = date_raw

        body = _extract_text(payload)
        emails.append(
            {
                "message_id": msg["id"],
                "from": headers.get("from", ""),
                "subject": headers.get("subject", ""),
                "date": email_date,
                "snippet": full.get("snippet", ""),
                "body": body[:6000],
                "gmail_url": f"https://mail.google.com/mail/#all/{msg['id']}",
            }
        )
    return emails
