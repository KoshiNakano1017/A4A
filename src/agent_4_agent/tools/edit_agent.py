from google.adk.tools import FunctionTool
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# 出力先ルート: OUTPUT_PROJECT_ROOT（.env）未設定時は A4A ルート
_REPO_ROOT = Path(__file__).resolve().parents[3]
_OUTPUT_ROOT = Path(os.environ.get("OUTPUT_PROJECT_ROOT", str(_REPO_ROOT))).resolve()


def _safe_rel_path(p: str) -> str:
    p = p.strip().replace("\\", "/")
    if not p or p.startswith("/") or ".." in p.split("/"):
        raise ValueError(f"不正なパスです: {p}")
    return p

# ファイル作成用のカスタムツール
def create_agent_files(agent_name: str, agent_code: str) -> str:
    """新しいエージェントのディレクトリとファイルを作成する
    agent_name: エージェント名（英小文字+_）
    agent_code: エージェントのPythonコード
    戻り値: 成功/失敗メッセージ
    出力先: プロジェクトルート
    """
    try:
        _safe_rel_path(agent_name)
        env_path = _REPO_ROOT / "src" / "agent_4_agent" / ".env"
        agent_dir = _OUTPUT_ROOT / "agents" / agent_name
        # エージェントディレクトリを作成
        agent_dir.mkdir(parents=True, exist_ok=True)
        # __init__.pyファイルを作成
        (agent_dir / "__init__.py").write_text(
            "from .agent import root_agent\n__all__ = [\"root_agent\"]\n",
            encoding="utf-8",
        )
        # a2a_agent.pyファイルを作成
        (agent_dir / "a2a_agent.py").write_text(
            "from . import root_agent\n\n"
            "if __name__ == \"__main__\":\n"
            "    from a4a_lab.agent_activity import run_a2a_with_activity\n"
            "    run_a2a_with_activity(root_agent)\n",
            encoding="utf-8",
        )
        # agent.pyファイルを作成
        (agent_dir / "agent.py").write_text(agent_code, encoding="utf-8")

        # 実行ファイルの階層にある.envファイルをコピーしてここに配置（なければ空で作成）
        env_content = ""
        if env_path.is_file():
            env_content = env_path.read_text(encoding="utf-8", errors="replace")
        (agent_dir / ".env").write_text(env_content, encoding="utf-8")

        return f"成功: {agent_name} を作成しました ({agent_dir})"
    except Exception as e:
        return f"エラー: {str(e)}"
    
# ファイル取得用のカスタムツール
def get_agent_file(agent_name: str, file_name: str) -> str:
    """既存のエージェントファイルを取得する
    agent_name: エージェント名（英小文字+_）
    file_name: 取得するファイル名（例: agent.py）
    戻り値: ファイル内容またはエラーメッセージ
    参照先: プロジェクトルート
    """
    try:
        _safe_rel_path(agent_name)
        _safe_rel_path(file_name)
        file_path = _OUTPUT_ROOT / "agents" / agent_name / file_name
        if not file_path.is_file():
            return f"エラー: ファイルが存在しません ({file_path})"
        return file_path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        return f"エラー: {str(e)}"

# ファイル更新用のカスタムツール
def edit_agent_file(agent_name: str, file_name: str, new_code: str) -> str:
    """既存のエージェントファイルを編集する
    agent_name: エージェント名（英小文字+_）
    file_name: 編集するファイル名（例: agent.py）
    new_code: 新しいコード内容
    戻り値: 成功/失敗メッセージ
    出力先: プロジェクトルート
    """
    try:
        _safe_rel_path(agent_name)
        _safe_rel_path(file_name)
        file_path = _OUTPUT_ROOT / "agents" / agent_name / file_name
        if not file_path.is_file():
            return f"エラー: ファイルが存在しません ({file_path})"
        file_path.write_text(new_code, encoding="utf-8")
        return f"成功: {file_name} を更新しました ({file_path})"
    except Exception as e:
        return f"エラー: {str(e)}"
    

create_agent_files_tool = FunctionTool(func=create_agent_files)
get_agent_file_tool = FunctionTool(func=get_agent_file)
edit_agent_file_tool = FunctionTool(func=edit_agent_file)