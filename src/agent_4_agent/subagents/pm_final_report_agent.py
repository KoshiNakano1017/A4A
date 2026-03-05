from google.adk.agents.llm_agent import Agent
from ..tools import read_output_file_tool
import os
from dotenv import load_dotenv
load_dotenv()
MODEL = os.environ.get("MODEL", "gemini-3-flash-preview")

pm_final_report_instruction = """
あなたはpm_final_report_agentです。
member_agents の作業が終わったら、必ず最後にユーザーへ以下の形式で納品報告してください：

```
---納品---

## 作成したプログラム
- 設計書: XXX
- 概要: XXX

## 生成ファイル（OUTPUT_PROJECT_ROOT 配下）
- agents/XXX/agent.py
- agents/XXX/.env
- ...

## 使い方・次に調整できる点
- XXX
```

creator_agent / reviewer_agent が報告したファイルパスを列挙し、必要なら read_output_file で要点を確認してから報告する。
"""

pm_final_report_agent = Agent(
    name="pm_final_report_agent",
    model=MODEL,
    instruction=pm_final_report_instruction,
    tools=[read_output_file_tool],
)
