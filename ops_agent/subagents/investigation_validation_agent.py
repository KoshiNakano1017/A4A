"""企画フェーズ2番目: 企画案の裏付け検証用。investigation_agent と同じ役割・異なる名前。"""
from investigation_agent.agent import root_agent as _investigation
from google.adk.agents.llm_agent import Agent

# 同一の instruction/model で異なる名前のエージェントを作成（SequentialAgent は重複名を許可しないため）
investigation_validation_agent = Agent(
    name="investigation_validation_agent",
    model=_investigation.model,
    description="企画案の裏付け検証。一次情報に基づき企画の妥当性を検証する。",
    instruction=_investigation.instruction,
    tools=[],
)

__all__ = ["investigation_validation_agent"]
