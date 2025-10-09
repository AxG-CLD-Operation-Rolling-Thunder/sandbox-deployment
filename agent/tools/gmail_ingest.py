
#!/usr/bin/env python3
"""
Gmail Ingest (Sent Mail → JSONL)
- Authenticates via OAuth (credentials.json → token.json).
- Pulls messages from the user's **Sent** mailbox (default last 6 months).
- Normalizes each message to a compact record with useful fields.
- Writes newline-delimited JSON (JSONL) for easy downstream loading (RAG, etc.).

"""

from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
from typing import Dict, Any, Iterable, List, Optional

from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime

from dateutil.relativedelta import relativedelta

# Google client libs
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pickle

# Gmail scopes — readonly is sufficient for ingestion
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
DEFAULT_OUT = "sent_emails.jsonl"


def load_creds(credentials_path: Path, token_path: Path):
    """Load or create user credentials via OAuth; return google-auth creds object."""
    creds = None
    if token_path.exists():
        with token_path.open("rb") as f:
            creds = pickle.load(f)
    if not creds:
        if not credentials_path.exists():
            raise FileNotFoundError(
                f"credentials.json not found at {credentials_path}. "
                "Create an OAuth Client (Desktop) in Google Cloud Console and download it here."
            )
        flow = InstalledAppFlow.from_client_secrets_file(str(credentials_path), SCOPES)
        creds = flow.run_local_server(port=0)
        with token_path.open("wb") as token:
            pickle.dump(creds, token)
    return creds


def gmail_service(creds):
    return build("gmail", "v1", credentials=creds)


def gmail_query_since(since: datetime | None) -> str:
    """Compose a Gmail search string for Sent items since a given date.
    We do NOT include label in the query because we pass labelIds=['SENT'] separately.
    """
    if since is None:
        since = datetime.now().astimezone() - relativedelta(months=6)
    # Gmail query date format can be yyyy/mm/dd
    q_date = since.strftime("%Y/%m/%d")
    return f"after:{q_date}"


def list_message_ids(
    service,
    user_id: str = "me",
    label_ids: Optional[List[str]] = None,
    query: Optional[str] = None,
    max_results: Optional[int] = None,
) -> List[str]:
    """Return a list of message IDs for a label/query, paginating as needed."""
    label_ids = label_ids or []
    msg_ids: List[str] = []
    page_token = None
    fetched = 0

    while True:
        kwargs = {
            "userId": user_id,
            "labelIds": label_ids,
            "q": query or "",
            "pageToken": page_token,
            "maxResults": min(500, max_results - fetched) if max_results else 500,
        }
        # Remove None entries to avoid API errors
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        resp = service.users().messages().list(**kwargs).execute()
        ids = [m["id"] for m in resp.get("messages", [])]
        msg_ids.extend(ids)
        fetched += len(ids)
        page_token = resp.get("nextPageToken")

        if (max_results and fetched >= max_results) or not page_token:
            break

    return msg_ids


def get_message(service, msg_id: str) -> Dict[str, Any]:
    return (
        service.users()
        .messages()
        .get(userId="me", id=msg_id, format="full")
        .execute()
    )


def _header(headers: List[Dict[str, str]], name: str) -> Optional[str]:
    for h in headers:
        if h.get("name", "").lower() == name.lower():
            return h.get("value")
    return None


def _body_plain_from_payload(payload: Dict[str, Any]) -> str:
    """Extract a best-effort plain text body from the message payload.
    Handles text/plain parts first, falls back to decoding text/html stripped tags minimalistic.
    """
    import base64
    import re

    def decode_part(part: Dict[str, Any]) -> str:
        data = part.get("body", {}).get("data")
        if not data:
            return ""
        # Gmail uses URL-safe base64
        raw = base64.urlsafe_b64decode(data.encode("utf-8"))
        return raw.decode("utf-8", errors="replace")

    def html_to_text(html: str) -> str:
        # Naive HTML → text strip (good enough for patterns/RAG). Avoids external deps.
        text = re.sub(r"<\s*br\s*/?>", "\n", html, flags=re.I)
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    mime_type = payload.get("mimeType", "")
    if mime_type == "text/plain":
        return decode_part(payload)

    if mime_type == "text/html":
        return html_to_text(decode_part(payload))

    # Multipart: search parts, prefer text/plain
    if mime_type.startswith("multipart/"):
        parts = payload.get("parts", [])
        plain = ""
        html = ""
        for p in parts:
            mt = p.get("mimeType", "")
            if mt == "text/plain" and not plain:
                plain = decode_part(p)
            elif mt == "text/html" and not html:
                html = html_to_text(decode_part(p))
        return plain or html or ""

    # Fallback: try body directly
    return decode_part(payload)


def normalize_message(msg: Dict[str, Any]) -> Dict[str, Any]:
    payload = msg.get("payload", {})
    headers = payload.get("headers", [])

    message_id = _header(headers, "Message-Id") or _header(headers, "Message-ID")
    subject = _header(headers, "Subject")
    date_raw = _header(headers, "Date")
    from_raw = _header(headers, "From")
    to_raw = _header(headers, "To")
    cc_raw = _header(headers, "Cc")
    in_reply_to = _header(headers, "In-Reply-To")
    references = _header(headers, "References")

    try:
        date_parsed = parsedate_to_datetime(date_raw) if date_raw else None
        if date_parsed and date_parsed.tzinfo is None:
            date_parsed = date_parsed.replace(tzinfo=timezone.utc)
    except Exception:
        date_parsed = None

    body_plain = _body_plain_from_payload(payload)

    return {
        "gmail_id": msg.get("id"),
        "thread_id": msg.get("threadId"),
        "message_id": message_id,
        "date": date_parsed.isoformat() if date_parsed else None,
        "subject": subject,
        "from": from_raw,
        "to": to_raw,
        "cc": cc_raw,
        "in_reply_to": in_reply_to,
        "references": references,
        "snippet": msg.get("snippet"),
        "body_plain": body_plain,
        "size_estimate": msg.get("sizeEstimate"),
        "label_ids": msg.get("labelIds"),
    }


def write_jsonl(records: Iterable[Dict[str, Any]], out_path: Path) -> int:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with out_path.open("w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            n += 1
    return n


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description="Ingest Gmail Sent messages into JSONL for RAG/persona analysis."
    )
    ap.add_argument(
        "--since",
        type=str,
        default=None,
        help="ISO date (YYYY-MM-DD). Default is 6 months ago.",
    )
    ap.add_argument(
        "--max",
        type=int,
        default=None,
        help="Max messages to fetch (across pages).",
    )
    ap.add_argument(
        "--out",
        type=str,
        default=DEFAULT_OUT,
        help=f"Output JSONL path (default: {DEFAULT_OUT}).",
    )
    ap.add_argument(
        "--query",
        type=str,
        default=None,
        help=(
            "Additional Gmail search syntax appended to the default 'after:DATE'. "
            "E.g., --query 'subject:(invoice) OR to:vendor@x.com'"
        ),
    )
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="List counts and a few IDs only; do not download or write a file.",
    )
    ap.add_argument(
        "--credentials",
        type=str,
        default="credentials.json",
        help="Path to OAuth client credentials.json",
    )
    ap.add_argument(
        "--token",
        type=str,
        default="token.json",
        help="Path to cached OAuth token.json",
    )
    return ap.parse_args()


def main():
    args = parse_args()

    # Resolve since date
    if args.since:
        try:
            since_dt = datetime.fromisoformat(args.since)
        except ValueError:
            raise SystemExit("--since must be in YYYY-MM-DD format")
    else:
        since_dt = None  # computed in gmail_query_since

    credentials_path = Path(args.credentials)
    token_path = Path(args.token)

    try:
        creds = load_creds(credentials_path, token_path)
        service = gmail_service(creds)

        # Compose query: always restrict to Sent via label; date filter via query
        date_q = gmail_query_since(since_dt)
        full_query = date_q
        if args.query:
            # Combine by space (Gmail treats as AND). Parentheses if you need complex OR.
            full_query = f"{date_q} {args.query}".strip()

        # 1) List IDs only (fast)
        ids = list_message_ids(
            service,
            user_id="me",
            label_ids=["SENT"],
            query=full_query,
            max_results=args.max,
        )

        if args.dry_run:
            print(f"[DRY-RUN] Matched {len(ids)} messages in Sent with query: '{full_query}'")
            print("Sample IDs:", ids[:10])
            return

        # 2) Fetch and normalize
        records: List[Dict[str, Any]] = []
        for i, mid in enumerate(ids, start=1):
            try:
                msg = get_message(service, mid)
                rec = normalize_message(msg)
                records.append(rec)
                if i % 50 == 0:
                    print(f"Fetched {i}/{len(ids)}…")
            except HttpError as e:
                print(f"Warning: failed to fetch {mid}: {e}")

        # 3) Write JSONL
        out_path = Path(args.out)
        n = write_jsonl(records, out_path)
        print(f"Wrote {n} messages to {out_path}")
        print("Done.")

    except HttpError as e:
        print(f"Gmail API error: {e}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
