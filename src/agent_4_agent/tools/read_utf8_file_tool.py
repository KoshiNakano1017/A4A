from google.adk.tools.function_tool import FunctionTool

def read_utf8_file(file_path: str) -> str:
    """UTF-8でファイルを読み込みます。
    
    Args:
        file_path: 読み込むファイルのパス
        
    Returns:
        ファイルの内容
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error: {str(e)}"


# FunctionToolとして登録
read_utf8_file_tool = FunctionTool(func=read_utf8_file)
