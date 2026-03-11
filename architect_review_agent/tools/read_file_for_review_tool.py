"""他エージェントが作成した資料・コードをレビュー用に読み込むツール。"""
from pathlib import Path

from google.adk.tools.function_tool import FunctionTool

# プロジェクトルート（docs/ の親）
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def _path_under_root(target: Path, root: Path) -> bool:
    """target が root 以下にあるか（パストラバーサル対策）。"""
    try:
        target.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def read_file_for_review(file_path: str) -> dict:
    """プロジェクト内のファイルを読み取り、レビュー用に内容を返す。

    設計書（docs/system_dev/）やソース（src/）など、プロジェクト配下のファイルを読む。

    Args:
        file_path: プロジェクトルートからの相対パス（例: docs/system_dev/er_diagram_xxx.md, src/main.py）、
                   または絶対パス（プロジェクト内に限る）。

    Returns:
        success, path, content（成功時）または success, error（失敗時）
    """
    try:
        base = _PROJECT_ROOT.resolve()
        path_input = file_path.strip().replace("\\", "/")
        if path_input.startswith("/") or (len(path_input) >= 2 and path_input[1] == ":"):
            target = Path(file_path).resolve()
            if not _path_under_root(target, base):
                return {
                    "success": False,
                    "error": f"パスがプロジェクト外を指しています: {file_path}",
                }
        else:
            target = (base / path_input.lstrip("/")).resolve()
            if not _path_under_root(target, base):
                return {
                    "success": False,
                    "error": f"パスがプロジェクト外を指しています: {file_path}",
                }
        if not target.is_file():
            return {
                "success": False,
                "error": f"ファイルが見つかりません: {target}",
            }
        content = target.read_text(encoding="utf-8", errors="replace")
        return {
            "success": True,
            "path": str(target),
            "content": content,
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


read_file_for_review_tool = FunctionTool(func=read_file_for_review)
