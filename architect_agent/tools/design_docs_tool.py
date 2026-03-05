"""設計成果物を docs/system_dev/ に格納するツール。ワンソース・マルチユースのためファイル名は役割名のみ（v1/v2/v3/Final は付けない）。"""
import os
import re
import sys
from datetime import datetime
from pathlib import Path

from google.adk.tools.function_tool import FunctionTool

# ターミナルに作業内容を表示（ポート指定で起動したエージェントのターミナルに出力）
_ACTIVITY_LABELS = {
    "flow_diagram": "フロー図作成中",
    "er_diagram": "ER図作成中",
    "user_manual": "ユーザーマニュアル作成中",
    "screen_definition": "画面項目定義書作成中",
    "screen_transition": "画面遷移図作成中",
    "requirements_spec": "要求仕様作成中",
    "requirements_definition": "要件定義書作成中",
}

# 出力先ルート: 環境変数 OUTPUT_PROJECT_ROOT が設定されていればそのパス、なければ A4A ルート
_A4A_ROOT = Path(__file__).resolve().parent.parent.parent
_OUTPUT_ROOT = Path(os.environ.get("OUTPUT_PROJECT_ROOT", _A4A_ROOT))
_DOCS_DIR = _OUTPUT_ROOT / "docs" / "system_dev"
# 旧版アーカイブ用ルート（docs/system_dev/old/{doc_type}/）
_OLD_ROOT_DIR = _DOCS_DIR / "old"

# ファイル名からバージョン表記を除去（ワンソース・マルチユース。バージョン管理は Git で行う）
_VERSION_PREFIX_PATTERN = re.compile(r"^(v\d+_|V\d+_)", re.IGNORECASE)
_VERSION_SUFFIX_PATTERN = re.compile(r"(_Final|_v\d+)$", re.IGNORECASE)


def _canonical_title(title: str) -> str:
    """役割名のみに正規化（v1/v2/v3/Final を除去）。"""
    s = title.strip()
    s = _VERSION_PREFIX_PATTERN.sub("", s)
    s = _VERSION_SUFFIX_PATTERN.sub("", s)
    return s.strip("_ ")

# キーワード→ファイル名プレフィックス・拡張子のルール
DOC_TYPE_MAP = {
    "flow_diagram": ("flow_diagram", "md"),
    "er_diagram": ("er_diagram", "md"),
    "user_manual": ("user_manual", "md"),
    "screen_definition": ("screen_item_definition", "md"),
    "screen_transition": ("screen_transition", "md"),
    "requirements_spec": ("requirements_spec", "md"),  # PM用: 企画完了時の要求仕様
    "requirements_definition": ("requirements_definition", "md"),  # アーキテクト用: 要件定義書
}


def write_design_doc(doc_type: str, title: str, content: str, suffix: str = "") -> dict:
    """設計成果物を docs/system_dev に保存する。old/<doc_type> への自動アーカイブと正本管理を行う。

    - アーカイブ構造: docs/system_dev/old/<doc_type>/ を自動作成する（例: docs/system_dev/old/er_diagram/）。
    - 「保存前」の自動アーカイブ: docs/system_dev 直下に同名ファイルが既に存在する場合、そのファイルを削除せず docs/system_dev/old/<doc_type>/ へ移動する。
      移動時のファイル名には作成日時を付与し、重複を防ぐ（例: er_diagram_Main_20240520_1800.md）。
    - 正本の固定: suffix の有無にかかわらず、docs/system_dev 直下には常にバージョン表記のない固定ファイル名で最新版1ファイルのみが存在する。
    - 成功時は「旧版を /old/<doc_type>/ フォルダにアーカイブし、最新版を正本として保存しました」または「最新版を正本として保存しました」を含むメッセージを返す。
    出力先ルートは環境変数 OUTPUT_PROJECT_ROOT で変更可能（未設定時は A4A プロジェクト内）。

    Args:
        doc_type: flow_diagram | er_diagram | user_manual | screen_definition | screen_transition | requirements_spec | requirements_definition
        title: ドキュメントのタイトル（ファイル名の一部に使用）
        content: 本文（Markdown または Mermaid 等）
        suffix: （廃止）ファイル名には使用しない。後方互換のため引数は残す。

    Returns:
        保存結果（path, success, message）
    """
    if doc_type not in DOC_TYPE_MAP:
        return {
            "success": False,
            "path": None,
            "message": f"不明な doc_type: {doc_type}. 利用可能: {list(DOC_TYPE_MAP.keys())}",
        }
    label = _ACTIVITY_LABELS.get(doc_type, "設計成果物作成中")
    print(f"[architect_agent] {label}", flush=True)
    sys.stdout.flush()
    prefix, ext = DOC_TYPE_MAP[doc_type]
    _DOCS_DIR.mkdir(parents=True, exist_ok=True)
    # doc_type ごとの旧版アーカイブ先（docs/system_dev/old/{doc_type}/）
    old_type_dir = _OLD_ROOT_DIR / doc_type
    old_type_dir.mkdir(parents=True, exist_ok=True)
    canonical = _canonical_title(title)
    safe_title = "".join(c if c.isalnum() or c in "-_" else "_" for c in canonical)[:80]
    # 最新版は常に日付なしの固定ファイル名（プレフィックス＋役割名のみ）。suffix は使用しない。
    fname = f"{prefix}_{safe_title}.{ext}".strip("_")
    path = _DOCS_DIR / fname
    archived = False
    try:
        # 保存前の自動アーカイブ: docs/system_dev 直下に同名ファイルがあれば old/{doc_type}/ へ日時付きで移動
        if path.exists():
            ts = datetime.now().strftime("%Y%m%d_%H%M")
            stem = path.stem
            archive_fname = f"{stem}_{ts}.{ext}"  # 作成日時付き、元の拡張子を維持
            archive_path = old_type_dir / archive_fname
            path.rename(archive_path)
            archived = True
        path.write_text(content, encoding="utf-8")
        # レビュー依頼で使いやすいよう相対パスも返す（プロジェクトルート基準）
        try:
            rel = path.resolve().relative_to(_OUTPUT_ROOT.resolve())
            relative_path = str(rel).replace("\\", "/")
        except ValueError:
            relative_path = str(path)
        detail = f"保存先: {path}。レビュー依頼時はパス「{relative_path}」を architect_review_agent に渡してください。"
        if archived:
            base_msg = (
                f"旧版を /old/{doc_type}/ フォルダにアーカイブし、最新版を正本として保存しました。{detail}"
            )
        else:
            base_msg = f"最新版を正本として保存しました。{detail}"
        return {
            "success": True,
            "path": str(path),
            "relative_path": relative_path,
            "message": base_msg,
        }
    except Exception as e:
        return {
            "success": False,
            "path": str(path),
            "message": str(e),
        }


def read_design_doc(file_path_or_name: str) -> dict:
    """設計成果物（docs/system_dev 内のファイル）を読み取り、内容をテキストで返す。
    レビューエージェントが設計書を読み取るために使用する。

    Args:
        file_path_or_name: ファイル名（例: er_diagram_Main.md）またはパス（例: docs/system_dev/er_diagram_Main.md）。
                           パスの場合はプロジェクトルート基準。読み取りは docs/system_dev 内に限定される。

    Returns:
        success: 成否
        content: ファイル本文（成功時）。失敗時は None
        path: 読み取ったファイルの絶対パス
        message: 結果メッセージ（失敗時はエラー内容）
    """
    path = Path(file_path_or_name)
    if not path.is_absolute():
        if "/" in file_path_or_name or "\\" in file_path_or_name:
            path = (_OUTPUT_ROOT / file_path_or_name).resolve()
        else:
            path = (_DOCS_DIR / file_path_or_name).resolve()
    else:
        path = path.resolve()
    _docs_resolved = _DOCS_DIR.resolve()
    try:
        if path == _docs_resolved or _docs_resolved not in path.parents:
            return {
                "success": False,
                "content": None,
                "path": str(path),
                "message": "読み取りは docs/system_dev 内のファイルに限定されています。",
            }
        if not path.exists():
            return {
                "success": False,
                "content": None,
                "path": str(path),
                "message": f"ファイルが存在しません: {path}",
            }
        if not path.is_file():
            return {
                "success": False,
                "content": None,
                "path": str(path),
                "message": "ディレクトリではなくファイルを指定してください。",
            }
        content = path.read_text(encoding="utf-8")
        return {
            "success": True,
            "content": content,
            "path": str(path),
            "message": f"読み取りました: {path}（{len(content)} 文字）",
        }
    except Exception as e:
        return {
            "success": False,
            "content": None,
            "path": str(path),
            "message": str(e),
        }


write_design_doc_tool = FunctionTool(func=write_design_doc)
read_design_doc_tool = FunctionTool(func=read_design_doc)
