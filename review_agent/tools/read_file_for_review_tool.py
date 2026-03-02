"""他エージェントが作成した資料・コードをレビュー用に読み込むツール。"""
import os
from pathlib import Path

from google.adk.tools.function_tool import FunctionTool

# プロジェクトルート（architect の成果物と同じ基準）。環境変数で上書き可能
_ROOT = Path(__file__).resolve().parent.parent.parent
_PROJECT_ROOT = Path(os.environ.get("OUTPUT_PROJECT_ROOT", os.environ.get("PROJECT_ROOT", _ROOT)))


def _path_under_root(target: Path, root: Path) -> bool:
    """target が root 以下にあるか（パストラバーサル対策）。"""
    try:
        target.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def read_file_for_review(file_path: str) -> dict:
    """プロジェクト内のファイルを読み取り、レビュー用に内容を返す。

    他エージェント（architect_agent, engineer_agent 等）が作成した
    設計書・コードのパスが渡されたときに使用する。

    Args:
        file_path: プロジェクトルートからの相対パス（例: docs/system_dev/er_diagram_xxx.md）、
                   またはプロジェクトルート以下の絶対パス（例: C:\\...\\A4A\\docs\\system_dev\\xxx.md）。

    Returns:
        success, path, content（成功時）または success, error（失敗時）
    """
    try:
        base = _PROJECT_ROOT.resolve()
        path_input = file_path.strip().replace("\\", "/")
        # 絶対パスで渡された場合: プロジェクトルート以下ならそのまま使用
        if path_input.startswith("/") or (len(path_input) >= 2 and path_input[1] == ":"):
            target = Path(file_path).resolve()
            if not _path_under_root(target, base):
                return {
                    "success": False,
                    "error": f"パスがプロジェクト外を指しています: {file_path}",
                }
        else:
            # 相対パス
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
