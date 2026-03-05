"""実装したソースコードを OUTPUT_PROJECT_ROOT に提出するツール。"""
import os
import sys
from pathlib import Path

from google.adk.tools.function_tool import FunctionTool

_A4A_ROOT = Path(__file__).resolve().parent.parent.parent
_OUTPUT_ROOT = Path(os.environ.get("OUTPUT_PROJECT_ROOT", _A4A_ROOT))


def _path_under_root(target: Path, root: Path) -> bool:
    """target が root 以下にあるか（パストラバーサル対策）。"""
    try:
        target.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def write_source(file_path: str, content: str) -> dict:
    """実装したソースコードを OUTPUT_PROJECT_ROOT に保存する。

    .env の OUTPUT_PROJECT_ROOT（例: C:/Users/nakano-koshi/project）を
    ルートとして、指定した相対パスにファイルを書き込む。
    パストラバーサル対策のため、OUTPUT_PROJECT_ROOT 外への書き込みは拒否する。

    Args:
        file_path: OUTPUT_PROJECT_ROOT からの相対パス（例: src/login.py, backend/api/handlers.py）
        content: ファイルの内容（ソースコード等）

    Returns:
        success: 成否
        path: 保存したファイルの絶対パス（成功時）
        message: 結果メッセージ
    """
    try:
        base = _OUTPUT_ROOT.resolve()
        path_input = file_path.strip().replace("\\", "/").lstrip("/")
        if not path_input:
            return {
                "success": False,
                "path": None,
                "message": "file_path を指定してください。",
            }
        target = (base / path_input).resolve()
        if not _path_under_root(target, base):
            return {
                "success": False,
                "path": str(target),
                "message": f"OUTPUT_PROJECT_ROOT 外への書き込みはできません: {file_path}",
            }
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        print(f"[engineer_agent] ソースコード提出: {target}", flush=True)
        sys.stdout.flush()
        return {
            "success": True,
            "path": str(target),
            "message": f"保存しました: {target}",
        }
    except Exception as e:
        return {
            "success": False,
            "path": None,
            "message": str(e),
        }


write_source_tool = FunctionTool(func=write_source)
