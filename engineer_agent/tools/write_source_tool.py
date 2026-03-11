"""実装したソースコードをプロジェクトルートに保存するツール。"""
import sys
from pathlib import Path

from google.adk.tools.function_tool import FunctionTool

# プロジェクトルート（A4A リポジトリのルート）
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def _path_under_root(target: Path, root: Path) -> bool:
    """target が root 以下にあるか（パストラバーサル対策）。"""
    try:
        target.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def write_source(file_path: str, content: str) -> dict:
    """実装したソースコードをプロジェクトのルート配下に保存する。

    出力先: プロジェクトルート（固定）。例: src/main.py → プロジェクト/src/main.py

    Args:
        file_path: プロジェクトルートからの相対パス（例: src/login.py, src/gui/app.py）
        content: ファイルの内容

    Returns:
        success, path, message
    """
    path_input = file_path.strip().replace("\\", "/").lstrip("/")
    if not path_input:
        return {
            "success": False,
            "path": None,
            "message": "file_path を指定してください。",
        }

    base = _PROJECT_ROOT.resolve()
    target = (base / path_input).resolve()
    if not _path_under_root(target, base):
        return {
            "success": False,
            "path": str(target),
            "message": f"プロジェクト外への書き込みはできません: {file_path}",
        }

    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        abs_path = str(target.resolve())
        print(f"[engineer_agent] 保存完了 → {abs_path}", flush=True)
        sys.stdout.flush()
        return {
            "success": True,
            "path": abs_path,
            "message": f"保存しました: {abs_path}",
        }
    except Exception as e:
        return {
            "success": False,
            "path": None,
            "message": str(e),
        }


write_source_tool = FunctionTool(func=write_source)
