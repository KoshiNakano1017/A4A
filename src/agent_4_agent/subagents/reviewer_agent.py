from google.adk.agents.llm_agent import Agent
from ..tools import write_source_tool, read_output_file_tool
import os
from dotenv import load_dotenv
load_dotenv()
MODEL = os.environ.get("MODEL", "gemini-3-flash-preview")

reviewer_instruction = """
あなたはreviewer_agentです。
creator_agent が作成したプログラムをレビューし、改善します。

【手順】
1. PMの指示と creator_agent の出力を確認する（作成したファイルパス一覧を把握）
2. read_output_file で各ソースファイルの内容を読み取る
3. 設計書との整合性・コード品質・セキュリティ・エラーハンドリング等を確認する
4. 改善点があれば write_source で上書き保存する
5. PMに「レビュー結果 + 修正したポイント + 次の改善案」を報告する

【観点】
- 設計書からの逸脱がないか
- 型・バリデーション・エラーハンドリングの不足
- セキュリティ（インジェクション、機密情報漏洩等）
- 可読性・保守性
"""

reviewer_agent = Agent(
    name="reviewer_agent",
    model=MODEL,
    instruction=reviewer_instruction,
    tools=[read_output_file_tool, write_source_tool]
)
