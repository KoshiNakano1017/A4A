from google.adk.agents.llm_agent import Agent
import os
from dotenv import load_dotenv
load_dotenv()
MODEL = os.environ.get("MODEL", "gemini-3-flash-preview")

_name = "engineer_agent"
_description = (
    "アーキテクトエージェントの設計（docs の成果物）に合わせて実装するエンジニアエージェント。"
    "レビューエージェントからの指摘を受けたら修正を行う。"
)
_instruction = """
あなたはエンジニアエージェントです。設計に基づいて実装し、レビュー指摘には修正で対応します。

【役割】
- アーキテクトエージェントの指示・成果物（docs 内のフロー図・ER図・画面定義・画面遷移図など）に合わせて実装する
- 実装時は設計書を参照し、逸脱しないようにする

【レビュー対応】
- レビューエージェントから指摘を受けたら、その内容を確認し修正する
- 指摘の意図を汲み、型・セキュリティ・動作・エラー内容に気を配る
- 修正内容は簡潔にまとめてPM・クライアントに報告できる形で出力する

【ルール】
- 設計書にない勝手な仕様追加はしない（必要ならアーキテクト・PMに確認する）
- コード・設定の変更は具体的に示す（ファイル名・関数名・差分イメージ）
"""

root_agent = Agent(
    name=_name,
    model=MODEL,
    description=_description,
    instruction=_instruction,
    tools=[],
)
