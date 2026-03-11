"""Google Drive へ設計書・ソースを出力する共通モジュール（非使用・廃止予定）。

設計書・ソースはプロジェクトの docs/ 配下に固定出力する方針のため、
本モジュールは現在使用されていません。将来的に削除予定です。
"""
from __future__ import annotations

import os
from pathlib import Path

# オプショナル: Drive API が無い環境では import 時に落とさない
try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from google.auth import default as google_default
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaInMemoryUpload
    _DRIVE_AVAILABLE = True
except ImportError:
    _DRIVE_AVAILABLE = False

SCOPES = ["https://www.googleapis.com/auth/drive"]


def _get_drive_service():
    """Drive API v3 のサービスを取得。ADC または OAuth を使用。"""
    if not _DRIVE_AVAILABLE:
        raise RuntimeError(
            "Google Drive 出力には google-api-python-client, google-auth-oauthlib が必要です。"
            " uv add google-api-python-client google-auth-oauthlib で追加してください。"
        )
    creds = None
    token_path = Path(__file__).resolve().parent.parent / "token.json"
    credentials_path = Path(__file__).resolve().parent.parent / "credentials.json"
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        elif credentials_path.exists():
            flow = InstalledAppFlow.from_client_secrets_file(str(credentials_path), SCOPES)
            creds = flow.run_local_server(port=0)
            with open(token_path, "w") as f:
                f.write(creds.to_json())
        else:
            creds, _ = google_default(scopes=SCOPES)
    return build("drive", "v3", credentials=creds)


def _get_or_create_folder(service, parent_id: str, name: str) -> str:
    """親フォルダ ID の下で、名前が name のフォルダの ID を返す。無ければ作成。"""
    q = f"'{parent_id}' in parents and name = '{name}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    r = service.files().list(q=q, spaces="drive", fields="files(id, name)").execute()
    files = r.get("files", [])
    if files:
        return files[0]["id"]
    body = {"name": name, "mimeType": "application/vnd.google-apps.folder", "parents": [parent_id]}
    f = service.files().create(body=body, fields="id").execute()
    return f["id"]


def _ensure_parent_folders(service, root_folder_id: str, relative_path: str) -> str:
    """例: 'docs/system_dev' なら root の下に docs → system_dev を作成し、最後のフォルダ ID を返す。"""
    parts = [p for p in relative_path.replace("\\", "/").split("/") if p]
    if not parts:
        return root_folder_id
    current = root_folder_id
    for name in parts:
        current = _get_or_create_folder(service, current, name)
    return current


def upload_to_drive(
    root_folder_id: str,
    relative_path: str,
    content: str,
    mime_type: str = "text/plain",
) -> dict:
    """指定した Drive フォルダ（root_folder_id）の下に、相対パスでファイルをアップロードする。

    relative_path 例: docs/system_dev/er_diagram_Main.md, src/main.py
    必要な親フォルダは自動作成する。

    Returns:
        success, file_id, web_view_link, message を含む dict
    """
    if not root_folder_id or not root_folder_id.strip():
        return {
            "success": False,
            "file_id": None,
            "web_view_link": None,
            "message": "OUTPUT_GOOGLE_DRIVE_FOLDER_ID が空です。",
        }
    relative_path = relative_path.strip().replace("\\", "/").lstrip("/")
    if not relative_path:
        return {
            "success": False,
            "file_id": None,
            "web_view_link": None,
            "message": "relative_path を指定してください。",
        }
    try:
        service = _get_drive_service()
    except Exception as e:
        return {
            "success": False,
            "file_id": None,
            "web_view_link": None,
            "message": f"Drive 認証エラー: {e}",
        }
    parts = relative_path.replace("\\", "/").split("/")
    if len(parts) == 1:
        parent_id = root_folder_id
        file_name = parts[0]
    else:
        parent_path = "/".join(parts[:-1])
        file_name = parts[-1]
        parent_id = _ensure_parent_folders(service, root_folder_id, parent_path)

    # 同名ファイルがあれば更新、なければ新規作成
    q = f"'{parent_id}' in parents and name = '{file_name}' and trashed = false"
    r = service.files().list(q=q, spaces="drive", fields="files(id, name)").execute()
    existing = r.get("files", [])
    media = MediaInMemoryUpload(content.encode("utf-8"), mimetype=mime_type, resumable=False)
    if existing:
        file_id = existing[0]["id"]
        service.files().update(fileId=file_id, media_body=media).execute()
    else:
        body = {"name": file_name, "parents": [parent_id]}
        f = service.files().create(body=body, media_body=media, fields="id, webViewLink").execute()
        file_id = f["id"]
        # webViewLink は create のレスポンスに含まれないことがあるので取得
    try:
        meta = service.files().get(fileId=file_id, fields="webViewLink").execute()
        web_view_link = meta.get("webViewLink") or f"https://drive.google.com/file/d/{file_id}/view"
    except Exception:
        web_view_link = f"https://drive.google.com/file/d/{file_id}/view"
    return {
        "success": True,
        "file_id": file_id,
        "web_view_link": web_view_link,
        "message": f"Drive に保存しました: {web_view_link}",
    }
