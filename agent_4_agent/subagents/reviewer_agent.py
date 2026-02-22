from google.adk.agents.llm_agent import Agent
from ..tools import create_agent_files_tool, edit_agent_file_tool, get_agent_file_tool
import os
from dotenv import load_dotenv
load_dotenv()
MODEL = os.environ.get("MODEL", "gemini-3-flash-preview")

# --- review_agent ---
reviewer_instruction = """
あなたはreviewer_agentです。
PMの要件と prepare_team_agent（searcher/surfer/creator）の出力を受け取り、最終生成物を改善してください。

目的:
- creator_agent が作った agent.py の _instruction に、
  searcher/surfer の # prompt_inserts を「自然に統合」して完成度を上げる。

[手順]
1. PMが決めたagent_name、goalを確認する
2. prepare_team_agentの出力を確認する
3. creator_agentが作成したエージェントコードをget_agent_file_toolを使って取得する
4. prepare_team_agentの出力内容を踏まえて、_description、_instructionを改善する
5. edit_agent_file_toolを使って、エージェントファイルを更新する
6. PMに「最終成果物の要約 + 更新したポイント + 次の改善案」を報告する
"""

reviewer_agent = Agent(
    name="reviewer_agent",
    model=MODEL,
    instruction=reviewer_instruction,
    tools=[get_agent_file_tool, edit_agent_file_tool]
)
