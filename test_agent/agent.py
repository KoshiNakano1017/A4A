from google.adk.agents.llm_agent import Agent
import os

_name = "test_agent"
_description = "test"
_instruction = "test"

root_agent = Agent(
    name=_name,
    model="gemini-3-flash-preview",
    description=_description,
    instruction=_instruction,
    tools=[],
)
