"""設計書に沿ったプログラムの入出力。プロジェクトルートを基準とする。"""
import sys
from pathlib import Path

from google.adk.tools.function_tool import FunctionTool

# プロジェクトルート
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def _path_under_root(target: Path, root: Path) -> bool:
    try:
        target.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def write_source(file_path: str, content: str) -> dict:
    """プログラムをプロジェクトルート配下に保存する。

    出力先: プロジェクトのルート（固定）。

    Args:
        file_path: プロジェクトルートからの相対パス（例: src/main.py）
        content: ファイル内容

    Returns:
        success, path, message
    """
    path_input = file_path.strip().replace("\\", "/").lstrip("/")
    if not path_input:
        return {"success": False, "path": None, "message": "file_path を指定してください。"}

    base = _PROJECT_ROOT.resolve()
    try:
        target = (base / path_input).resolve()
        if not _path_under_root(target, base):
            return {"success": False, "path": str(target), "message": f"プロジェクト外への書き込みはできません: {file_path}"}
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        abs_path = str(target.resolve())
        print(f"[creator_agent] 保存完了 → {abs_path}", flush=True)
        sys.stdout.flush()
        return {"success": True, "path": str(target), "message": f"保存しました: {target}"}
    except Exception as e:
        return {"success": False, "path": None, "message": str(e)}


def read_output_file(file_path: str) -> dict:
    """プロジェクト配下のファイルを読み取る。

    Args:
        file_path: プロジェクトルートからの相対パス（例: src/main.py）

    Returns:
        success, content, path, message
    """
    try:
        base = _PROJECT_ROOT.resolve()
        path_input = file_path.strip().replace("\\", "/").lstrip("/")
        if not path_input:
            return {"success": False, "content": None, "path": None, "message": "file_path を指定してください。"}
        target = (base / path_input).resolve()
        if not _path_under_root(target, base):
            return {"success": False, "content": None, "path": str(target), "message": f"プロジェクト外は読めません: {file_path}"}
        if not target.is_file():
            return {"success": False, "content": None, "path": str(target), "message": f"ファイルが存在しません: {target}"}
        content = target.read_text(encoding="utf-8", errors="replace")
        return {"success": True, "content": content, "path": str(target), "message": f"読み取りました: {target}"}
    except Exception as e:
        return {"success": False, "content": None, "path": None, "message": str(e)}


write_source_tool = FunctionTool(func=write_source)
read_output_file_tool = FunctionTool(func=read_output_file)
