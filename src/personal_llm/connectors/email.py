from __future__ import annotations

import imaplib
import mailbox
from email.message import EmailMessage
from pathlib import Path
from typing import Any

from personal_llm.config.settings import AppSettings
from personal_llm.core.io import (
    ensure_directory,
    materialize_raw_copy,
    sha256_file,
    sha256_text,
)
from personal_llm.core.schemas import SourceDocument, SourceType


class EmailConnector:
    def discover(
        self,
        settings: AppSettings,
        raw_dir: Path,
        connector_config: dict[str, Any],
    ) -> list[SourceDocument]:
        documents: list[SourceDocument] = []
        mbox_paths = connector_config.get("mbox_paths", [])
        if isinstance(mbox_paths, list):
            for mbox_path in mbox_paths:
                if not isinstance(mbox_path, str):
                    continue
                path = settings.resolve(mbox_path)
                if not path.exists():
                    continue
                snapshot_path = materialize_raw_copy(path, raw_dir, "email_exports")
                documents.append(
                    SourceDocument(
                        id=f"mbox::{path.as_posix()}",
                        source_type=SourceType.EMAIL_EXPORT,
                        uri=path.as_uri(),
                        title=path.name,
                        content_path=str(snapshot_path),
                        checksum=sha256_file(path),
                        metadata={
                            "format": "mbox",
                            "original_path": str(path),
                            "snapshot_path": str(snapshot_path),
                            "snapshot_strategy": "content_addressed_copy",
                        },
                    )
                )
        gmail_takeout_paths = connector_config.get("gmail_takeout_paths", [])
        if isinstance(gmail_takeout_paths, list):
            for takeout_path in gmail_takeout_paths:
                if not isinstance(takeout_path, str):
                    continue
                path = settings.resolve(takeout_path)
                if not path.exists():
                    continue
                snapshot_path = materialize_raw_copy(path, raw_dir, "gmail_takeout")
                documents.append(
                    SourceDocument(
                        id=f"gmail::{path.as_posix()}",
                        source_type=SourceType.EMAIL_EXPORT,
                        uri=path.as_uri(),
                        title=path.name,
                        content_path=str(snapshot_path),
                        checksum=sha256_file(path),
                        metadata={
                            "format": "gmail_takeout",
                            "original_path": str(path),
                            "snapshot_path": str(snapshot_path),
                            "snapshot_strategy": "content_addressed_copy",
                        },
                    )
                )
        imap_config = connector_config.get("imap", {})
        if isinstance(imap_config, dict) and imap_config.get("enabled"):
            documents.extend(
                self._sync_imap(
                    settings=settings,
                    raw_dir=raw_dir,
                    imap_config=imap_config,
                )
            )
        return documents

    def _sync_imap(
        self,
        settings: AppSettings,
        raw_dir: Path,
        imap_config: dict[str, Any],
    ) -> list[SourceDocument]:
        if not settings.imap_host or not settings.imap_username or not settings.imap_password:
            return []
        target_dir = ensure_directory(raw_dir / "imap")
        folder = str(imap_config.get("folder", "INBOX"))
        client = imaplib.IMAP4_SSL(settings.imap_host, settings.imap_port)
        client.login(settings.imap_username, settings.imap_password)
        client.select(folder)
        typ, data = client.search(None, "ALL")
        if typ != "OK":
            return []
        ids = data[0].split()
        documents: list[SourceDocument] = []
        for message_id in ids[-50:]:
            fetch_status, fetch_data = client.fetch(message_id, "(RFC822)")
            if fetch_status != "OK":
                continue
            raw_message = fetch_data[0][1]
            if not isinstance(raw_message, bytes):
                continue
            filename = f"{folder}-{message_id.decode('utf-8')}.eml"
            destination = target_dir / filename
            destination.write_bytes(raw_message)
            documents.append(
                SourceDocument(
                    id=f"imap::{folder}::{filename}",
                    source_type=SourceType.EMAIL_EXPORT,
                    uri=destination.as_uri(),
                    title=filename,
                    content_path=str(destination),
                    checksum=sha256_file(destination),
                    metadata={"format": "imap_eml", "folder": folder},
                )
            )
        return documents

    @staticmethod
    def summarize_message(message: EmailMessage) -> dict[str, Any]:
        return {
            "message_id": message.get("Message-ID"),
            "thread_id": sha256_text(
                (message.get("Subject") or "") + (message.get("In-Reply-To") or "")
            ),
            "subject": message.get("Subject"),
            "from": message.get("From"),
            "to": message.get("To"),
            "date": message.get("Date"),
            "attachment_count": sum(1 for part in message.walk() if part.get_filename()),
        }

    @staticmethod
    def read_mbox(path: Path) -> list[EmailMessage]:
        box = mailbox.mbox(path)
        messages: list[EmailMessage] = []
        for message in box:
            if isinstance(message, EmailMessage):
                messages.append(message)
            else:
                parser = EmailMessage()
                parser.set_content(message.as_string())
                messages.append(parser)
        return messages
