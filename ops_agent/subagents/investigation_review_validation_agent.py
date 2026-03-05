"""企画フェーズ5番目: レビュー内容の裏付け検証用。investigation_agent と同じ役割・異なる名前。"""
from investigation_agent.agent import root_agent as _investigation
from google.adk.agents.llm_agent import Agent

investigation_review_validation_agent = Agent(
    name="investigation_review_validation_agent",
    model=_investigation.model,
    description="レビュー内容の裏付け検証。企画Bの指摘が一次情報と整合するか検証する。",
    instruction=_investigation.instruction,
    tools=[],
)

__all__ = ["investigation_review_validation_agent"]
