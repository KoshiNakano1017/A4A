from google.adk.agents.llm_agent import Agent
import os

_name = "rag_contradiction_architect"
_description = "Design and prototype a Gemini RAG system with contradictory requirements."
_instruction = "Design and prototype a Gemini RAG system."

root_agent = Agent(
    name=_name,
    model="gemini-1.5-flash",
    description=_description,
    instruction=_instruction,
    tools=[],
)
