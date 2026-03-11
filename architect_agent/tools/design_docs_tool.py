"""設計成果物をプロジェクトの docs/system_dev/ に格納するツール。"""
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from google.adk.tools.function_tool import FunctionTool

# プロジェクトルート（A4A リポジトリのルート）= docs/ の親
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_DOCS_DIR = _PROJECT_ROOT / "docs" / "system_dev"
_MANIFEST_PATH = _DOCS_DIR / "_manifest.json"

# ターミナルに作業内容を表示
_ACTIVITY_LABELS = {
    "flow_diagram": "フロー図作成中",
    "er_diagram": "ER図作成中",
    "user_manual": "ユーザーマニュアル作成中",
    "screen_definition": "画面項目定義書作成中",
    "screen_transition": "画面遷移図作成中",
    "requirements_spec": "要求仕様作成中",
    "requirements_definition": "要件定義書作成中",
    "api_spec": "API仕様書作成中",
    "authz_design": "認証・認可設計作成中",
    "persistence_design": "永続化設計作成中",
    "vertex_ai_search_config": "Vertex AI Search 設定作成中",
    "rag_generation_spec": "RAG生成仕様作成中",
    "ops_design": "運用設計作成中",
}

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
    "api_spec": ("api_spec", "md"),
    "authz_design": ("authz_design", "md"),
    "persistence_design": ("persistence_design", "md"),
    "vertex_ai_search_config": ("vertex_ai_search_config", "md"),
    "rag_generation_spec": ("rag_generation_spec", "md"),
    "ops_design": ("ops_design", "md"),
}

def _now_ts() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M")


def _load_manifest(docs_dir: Path) -> dict[str, Any]:
    """docs/system_dev/_manifest.json を読み取る。なければ新規テンプレを返す。"""
    try:
        path = (docs_dir / _MANIFEST_PATH.name).resolve()
        if not path.exists():
            return {"schema_version": 1, "doc_types": {}}
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return {"schema_version": 1, "doc_types": {}}
        data.setdefault("schema_version", 1)
        data.setdefault("doc_types", {})
        if not isinstance(data["doc_types"], dict):
            data["doc_types"] = {}
        return data
    except Exception:
        return {"schema_version": 1, "doc_types": {}}


def _save_manifest(docs_dir: Path, manifest: dict[str, Any]) -> None:
    path = (docs_dir / _MANIFEST_PATH.name).resolve()
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _safe_title_from_title(title: str) -> str:
    canonical = _canonical_title(title)
    return "".join(c if c.isalnum() or c in "-_" else "_" for c in canonical)[:80]


def _resolve_fixed_filename(docs_dir: Path, doc_type: str, title: str) -> tuple[str, str, bool]:
    """doc_type ごとに固定ファイル名を決める（manifest で強制）。"""
    prefix, ext = DOC_TYPE_MAP[doc_type]
    manifest = _load_manifest(docs_dir)
    doc_types = manifest.get("doc_types", {})
    changed = False

    current = doc_types.get(doc_type)
    if not isinstance(current, dict):
        current = {}

    # 初回のみ title から canonical を採用し、以後固定する
    if "canonical_title" not in current or not current.get("canonical_title"):
        safe_title = _safe_title_from_title(title)
        current["canonical_title"] = safe_title or doc_type
        changed = True
    safe_title = str(current["canonical_title"])

    fname = f"{prefix}_{safe_title}.{ext}".strip("_")
    current["file_name"] = fname
    doc_types[doc_type] = current
    manifest["doc_types"] = doc_types
    manifest["updated_at"] = datetime.now().isoformat(timespec="seconds")

    if changed:
        _save_manifest(docs_dir, manifest)
    return fname, safe_title, changed


def _archive_path(old_type_dir: Path, stem: str, ext: str) -> Path:
    return (old_type_dir / f"{stem}_{_now_ts()}.{ext}").resolve()


def _archive_conflicting_same_type_files(
    docs_dir: Path,
    old_type_dir: Path,
    doc_type: str,
    keep_fname: str,
) -> list[str]:
    """docs/system_dev 直下の同種ファイルを強制的に old/<doc_type>/ に退避する。"""
    prefix, ext = DOC_TYPE_MAP[doc_type]
    archived: list[str] = []
    keep = (docs_dir / keep_fname).resolve()
    for p in docs_dir.glob(f"{prefix}_*.{ext}"):
        try:
            if p.resolve() == keep:
                continue
            if not p.is_file():
                continue
            archive_path = _archive_path(old_type_dir, p.stem, ext)
            p.rename(archive_path)
            archived.append(str(archive_path))
        except Exception:
            # 退避失敗は write の致命傷にしない（レビュー側で検知させる）
            continue
    return archived


def write_design_doc(doc_type: str, title: str, content: str, suffix: str = "") -> dict:
    """設計成果物を docs/system_dev に保存する。old/<doc_type> への自動アーカイブと正本管理を行う。

    - アーカイブ構造: docs/system_dev/old/<doc_type>/ を自動作成する（例: docs/system_dev/old/er_diagram/）。
    - 「保存前」の自動アーカイブ: docs/system_dev 直下に同名ファイルが既に存在する場合、そのファイルを削除せず docs/system_dev/old/<doc_type>/ へ移動する。
      移動時のファイル名には作成日時を付与し、重複を防ぐ（例: er_diagram_Main_20240520_1800.md）。
    - 正本の固定: suffix の有無にかかわらず、docs/system_dev 直下には常にバージョン表記のない固定ファイル名で最新版1ファイルのみが存在する。
    - 成功時は「旧版を /old/<doc_type>/ フォルダにアーカイブし、最新版を正本として保存しました」または「最新版を正本として保存しました」を含むメッセージを返す。
    出力先: プロジェクトの docs/system_dev/（固定）。

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
    _, ext = DOC_TYPE_MAP[doc_type]

    docs_dir = _DOCS_DIR.resolve()
    old_type_dir = (docs_dir / "old" / doc_type).resolve()
    path = (docs_dir / "UNKNOWN").resolve()
    fname = ""
    safe_title = ""
    manifest_changed = False
    conflict_archives: list[str] = []
    archived = False
    try:
        docs_dir.mkdir(parents=True, exist_ok=True)
        old_type_dir.mkdir(parents=True, exist_ok=True)
        fname, safe_title, manifest_changed = _resolve_fixed_filename(docs_dir, doc_type, title)
        path = (docs_dir / fname).resolve()

        # 同種ファイルの増殖を強制抑止（同 prefix の別ファイルは old/<doc_type>/ へ退避）
        conflict_archives = _archive_conflicting_same_type_files(
            docs_dir=docs_dir,
            old_type_dir=old_type_dir,
            doc_type=doc_type,
            keep_fname=fname,
        )
        if path.exists():
            archive_path = _archive_path(old_type_dir, path.stem, ext)
            path.rename(archive_path)
            archived = True
        path.write_text(content, encoding="utf-8")
        abs_path = str(path.resolve())
        print(f"[architect_agent] 保存完了 → {abs_path}", flush=True)
        sys.stdout.flush()
        relative_path = f"docs/system_dev/{fname}"
        title_note = (
            f"doc_type「{doc_type}」の正本ファイル名を固定しました（canonical_title={safe_title}）。"
            if manifest_changed
            else f"doc_type「{doc_type}」の正本ファイル名は固定です（canonical_title={safe_title}）。"
        )
        conflict_note = f" 同種ファイル退避: {len(conflict_archives)} 件。" if conflict_archives else ""
        detail = (
            f"{title_note}{conflict_note} 保存先: {abs_path}。"
            f"レビュー依頼時はパス「{relative_path}」を architect_review_agent に渡してください。"
        )
        base_msg = (
            f"旧版を /old/{doc_type}/ にアーカイブし、最新版を保存しました。{detail}"
            if archived
            else f"最新版を保存しました。{detail}"
        )
        return {
            "success": True,
            "path": abs_path,
            "relative_path": relative_path,
            "message": base_msg,
        }
    except Exception as e:
        return {"success": False, "path": str(path), "message": str(e)}


def read_design_doc(file_path_or_name: str) -> dict:
    """設計成果物（プロジェクトの docs/system_dev 内）を読み取り、内容をテキストで返す。
    レビュー時は docs/system_dev 内のパスを指定する。

    Args:
        file_path_or_name: ファイル名（例: er_diagram_Main.md）またはパス（例: docs/system_dev/er_diagram_Main.md）。
                           プロジェクトの docs/ 配下に限定。

    Returns:
        success: 成否
        content: ファイル本文（成功時）。失敗時は None
        path: 読み取ったファイルの絶対パス
        message: 結果メッセージ（失敗時はエラー内容）
    """
    path = Path(file_path_or_name)
    docs_dir = _DOCS_DIR.resolve()
    if not path.is_absolute():
        if "/" in file_path_or_name or "\\" in file_path_or_name:
            path = (_PROJECT_ROOT / file_path_or_name).resolve()
        else:
            path = (docs_dir / file_path_or_name).resolve()
    else:
        path = path.resolve()
    try:
        if path.resolve() == docs_dir or docs_dir not in path.parents:
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


def list_system_dev_docs() -> dict:
    """docs/system_dev 直下の設計書を列挙する（old/ 配下は除外）。"""
    docs_dir = _DOCS_DIR.resolve()
    files: list[str] = []
    if not docs_dir.exists():
        return {"success": True, "docs_dir": str(docs_dir), "files": []}
    for p in docs_dir.glob("*.md"):
        if p.name == _MANIFEST_PATH.name:
            continue
        if p.is_file():
            files.append(str(p))
    files.sort()
    return {"success": True, "docs_dir": str(docs_dir), "files": files}


_MERMAID_BLOCK_RE = re.compile(r"```mermaid\s*\n([\s\S]*?)\n```", re.MULTILINE)
_NODE_LABEL_UNQUOTED_RISK_RE = re.compile(r"^\s*([A-Za-z0-9_]+)\[([^\"]*?[()/][^\]]*?)\]\s*$")
_PSC_DEFINITION_RE = re.compile(
    r"\bPSC\b.*(Private\s+Service\s+Connect|プライベート.*サービス.*コネクト)", re.IGNORECASE
)


def _validate_mermaid(content: str) -> list[str]:
    warnings: list[str] = []
    for idx, m in enumerate(_MERMAID_BLOCK_RE.finditer(content), start=1):
        block = m.group(1)
        for ln, line in enumerate(block.splitlines(), start=1):
            s = line.strip()
            if not s or s.startswith("%%"):
                continue
            # node[label] で括弧やスラッシュが含まれる場合は "..." で囲むのを推奨
            mm = _NODE_LABEL_UNQUOTED_RISK_RE.match(line)
            if mm:
                node_id = mm.group(1)
                label = mm.group(2)
                warnings.append(
                    f"Mermaid block#{idx} line{ln}: ノード {node_id}[{label}] は記号を含むため {node_id}[\"...\"] 形式を推奨"
                )
    return warnings


def _validate_abbrev(content: str) -> list[str]:
    warnings: list[str] = []
    if "PSC" in content and not _PSC_DEFINITION_RE.search(content):
        warnings.append("略語 PSC が定義されていません（例: PSC = Private Service Connect）")
    return warnings


def validate_system_dev_docs() -> dict:
    """docs/system_dev の正本群に対して最低限の検査を行う（重複/略語/mermaid）。"""
    listed = list_system_dev_docs()
    if not listed.get("success"):
        return listed
    files: list[str] = listed["files"]

    # doc_type 重複検出（prefix 単位）
    prefix_to_doc_type = {v[0]: k for k, v in DOC_TYPE_MAP.items()}
    by_type: dict[str, list[str]] = {}
    unknown: list[str] = []
    for f in files:
        name = Path(f).name
        prefix = name.split("_", 1)[0]
        doc_type = prefix_to_doc_type.get(prefix)
        if not doc_type:
            unknown.append(f)
            continue
        by_type.setdefault(doc_type, []).append(f)

    duplicates = {k: v for k, v in by_type.items() if len(v) > 1}

    issues: list[dict[str, Any]] = []
    if duplicates:
        issues.append({"type": "duplicate_doc_type", "details": duplicates})
    if unknown:
        issues.append({"type": "unknown_prefix", "details": unknown})

    # 必須 doc_type の不足検出（上流〜下流で実装可能にするため）
    required_doc_types = [
        "requirements_definition",
        "flow_diagram",
        "er_diagram",
        "screen_definition",
        "api_spec",
        "authz_design",
        "persistence_design",
        "vertex_ai_search_config",
        "rag_generation_spec",
        "ops_design",
    ]
    missing = [dt for dt in required_doc_types if dt not in by_type]
    if missing:
        issues.append({"type": "missing_required_doc_type", "details": missing})

    file_findings: dict[str, Any] = {}
    for f in files:
        try:
            content = Path(f).read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            file_findings[f] = {"read_error": str(e)}
            continue
        mermaid = _validate_mermaid(content)
        abbrev = _validate_abbrev(content)
        if mermaid or abbrev:
            file_findings[f] = {"mermaid_warnings": mermaid, "abbrev_warnings": abbrev}

    ok = not issues and not file_findings
    return {
        "success": True,
        "ok": ok,
        "issues": issues,
        "file_findings": file_findings,
        "message": "OK" if ok else "issues found",
    }


list_system_dev_docs_tool = FunctionTool(func=list_system_dev_docs)
validate_system_dev_docs_tool = FunctionTool(func=validate_system_dev_docs)
