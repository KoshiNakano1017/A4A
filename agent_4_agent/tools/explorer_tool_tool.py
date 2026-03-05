from google.adk.tools.function_tool import FunctionTool

def explorer_tool(action: str, path: str = ".") -> str:
    """ディレクトリやファイルの内容を探索します。
    
    Args:
        action: "list" (ディレクトリ一覧) または "read" (ファイル読み込み)
        path: 対象のパス
        
    Returns:
        結果の文字列
    """
    import os
    try:
        if action == "list":
            if not os.path.exists(path):
                return f"Error: Path {path} does not exist."
            items = os.listdir(path)
            return "\n".join(items)
        elif action == "read":
            if not os.path.isfile(path):
                return f"Error: {path} is not a file."
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        else:
            return "Error: Unknown action. Use 'list' or 'read'."
    except Exception as e:
        return f"Error: {str(e)}"


# FunctionToolとして登録
explorer_tool_tool = FunctionTool(func=explorer_tool)
