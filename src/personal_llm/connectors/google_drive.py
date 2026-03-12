from __future__ import annotations

import io
import json
from pathlib import Path
from typing import Any

from personal_llm.config.settings import AppSettings
from personal_llm.core.io import ensure_directory, sha256_file
from personal_llm.core.schemas import SourceDocument, SourceType


class GoogleDriveConnector:
    def discover(self, settings: AppSettings, raw_dir: Path, connector_config: dict[str, Any]) -> list[SourceDocument]:
        if not connector_config.get("enabled"):
            return []
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaIoBaseDownload

        scope = ["https://www.googleapis.com/auth/drive.readonly"]
        token_path = settings.resolve(settings.google_drive_token)
        secret_path = settings.resolve(settings.google_drive_client_secret)
        credentials: Credentials | None = None
        if token_path.exists():
            credentials = Credentials.from_authorized_user_file(str(token_path), scope)
        if credentials is None or not credentials.valid:
            flow = InstalledAppFlow.from_client_secrets_file(str(secret_path), scope)
            credentials = flow.run_local_server(port=0)
            ensure_directory(token_path.parent)
            token_path.write_text(credentials.to_json(), encoding="utf-8")

        service = build("drive", "v3", credentials=credentials)
        target_dir = ensure_directory(raw_dir / "google_drive")
        root_folder_id = connector_config.get("root_folder_id")
        query = f"'{root_folder_id}' in parents and trashed = false" if root_folder_id else "trashed = false"
        response = service.files().list(
            q=query,
            pageSize=200,
            fields="files(id,name,mimeType,modifiedTime,md5Checksum,parents,webViewLink)",
        ).execute()
        export_mimetypes = connector_config.get("export_mimetypes", {})
        documents: list[SourceDocument] = []
        for item in response.get("files", []):
            file_id = item["id"]
            mime_type = item["mimeType"]
            filename = item["name"]
            destination = target_dir / filename
            if mime_type.startswith("application/vnd.google-apps"):
                if not isinstance(export_mimetypes, dict) or mime_type not in export_mimetypes:
                    continue
                export_media = service.files().export_media(fileId=file_id, mimeType=export_mimetypes[mime_type])
                extension = ".txt" if export_mimetypes[mime_type] == "text/plain" else ".csv"
                destination = target_dir / f"{filename}{extension}"
            else:
                export_media = service.files().get_media(fileId=file_id)
            with destination.open("wb") as handle:
                downloader = MediaIoBaseDownload(handle, export_media)
                done = False
                while not done:
                    _, done = downloader.next_chunk()
            documents.append(
                SourceDocument(
                    id=f"drive::{file_id}",
                    source_type=SourceType.GOOGLE_DRIVE,
                    uri=item.get("webViewLink") or destination.as_uri(),
                    title=filename,
                    content_path=str(destination),
                    checksum=sha256_file(destination),
                    metadata={
                        "google_drive_id": file_id,
                        "mime_type": mime_type,
                        "modified_time": item.get("modifiedTime"),
                        "parents": item.get("parents", []),
                    },
                )
            )
        self._write_state(target_dir / "state.json", response)
        return documents

    @staticmethod
    def _write_state(path: Path, response: dict[str, Any]) -> None:
        ensure_directory(path.parent)
        path.write_text(json.dumps(response, indent=2), encoding="utf-8")

