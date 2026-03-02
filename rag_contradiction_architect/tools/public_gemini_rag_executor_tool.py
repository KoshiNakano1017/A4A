from google.adk.tools.function_tool import FunctionTool

def public_gemini_rag_executor(query: str, api_key: str, context_text: str = "") -> str:
    \"\"\"
    パブリックなGemini APIを使用して、ローカル（社内）コンテキストに基づいた回答を生成します。
    ※このツールは、インターネット経由で外部API（Google AI Studio等）にアクセスします。
    
    Args:
        query: ユーザーの質問（マスキング済み推奨）
        api_key: Google AI Studio (Gemini API) の APIキー
        context_text: RAGのためのコンテキスト（社内ドキュメントの抜粋など、マスキング済み推奨）
        
    Returns:
        Gemini APIからの回答
    \"\"\"
    import google.generativeai as genai
    import os

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        prompt = f\"\"\"
        以下の社内向けに整理されたコンテキスト（一部マスキング済み）を参考にして、質問に答えてください。
        
        【コンテキスト】
        {context_text}
        
        【質問】
        {query}
        
        ※回答は社内関係者のみが閲覧することを想定してください。
        \"\"\"
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error connecting to public API: {str(e)}"


# FunctionToolとして登録
public_gemini_rag_executor_tool = FunctionTool(func=public_gemini_rag_executor)
