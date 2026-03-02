from google.adk.tools.function_tool import FunctionTool

def data_masker(text: str) -> str:
    \"\"\"
    社内情報（と思われる単語）をダミーデータに置き換え、
    パブリックAPIに送信しても問題ないようにマスキングします。
    ※本ツールはプロトタイプ用であり、完全な匿名化を保証するものではありません。

    Args:
        text: マスキング対象のテキスト

    Returns:
        マスキング後のテキスト
    \"\"\"
    import re
    # 簡易的なマスキング（例：社名や機密キーワードの置換）
    patterns = {
        r"自社": "[MASKED_COMPANY]",
        r"株式会社[A-Z]+": "[MASKED_PARTNER]",
        r"機密": "[CONFIDENTIAL]",
        r"\d{4,}-\d{2,}-\d{2,}": "[MASKED_DATE]"
    }
    
    masked_text = text
    for pattern, replacement in patterns.items():
        masked_text = re.sub(pattern, replacement, masked_text)
    
    return masked_text


# FunctionToolとして登録
data_masker_tool = FunctionTool(func=data_masker)
