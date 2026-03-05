from google.adk.agents.llm_agent import Agent
from google.adk.agents import ParallelAgent, SequentialAgent
from .subagents import (
    creator_agent,
    surfer_agent,
    searcher_agent,
    reviewer_agent,
    pm_final_report_agent,
    tool_creator_agent,
    prompt_engineer_agent,
    security_officer_agent,
)
import os
from dotenv import load_dotenv
load_dotenv()
MODEL = os.environ.get("MODEL", "gemini-3-flash-preview")


# --- PM（要件化＆タスク分解） ---
pm_instruction = """
あなたはPMエージェントです。
docs/system_dev/ の設計書に沿ったプログラム作成の要件を明確化するのが役割です。

【INPUT / OUTPUT】
- INPUT: docs/system_dev/ 配下の正本（設計書）。creator_agent に設計書パスを渡し、read_design_doc で読み取ってから作成させる。
- OUTPUT: 成果物はプロジェクトルート（OUTPUT_PROJECT_ROOT、.env で定義）に出力する。

【手順】
1. ユーザーの要望を確認する（どの設計書に基づくプログラムか、追加要件等）
2. 不明確な点があれば「合計1回だけ」質問してよい
3. docs/system_dev 内の該当設計書パスを特定する
4. 要件が固まったら「要件確定しました」と明示し、creator_agent に指示を出す
5. member_agents に作業を開始させる
6. reviewer_agent の完了報告を受け取ったら、ユーザーに「納品報告」を行う

【creator_agent への指示フォーマット】
```
# 要件確定

## 設計書パス（必ず read_design_doc で読み取ること）
docs/system_dev/xxx.md
（複数ある場合は列挙）

## 作成するプログラムの概要
- 何を作るか
- 出力先のディレクトリ構成（例: src/main.py, backend/api.py）
- 追加要件・制約

## research_brief（searcher/surfer 用・必要なら）
- 調べたい対象、ほしいアウトプット
```

"""

prepare_team_agent = ParallelAgent(
    name="prepare_team_agent",
    description="searcher/surfer/creator/tool_creator を並列に実行する。",
    sub_agents=[searcher_agent, surfer_agent, creator_agent, tool_creator_agent],
)


member_agents = SequentialAgent(
    name="member_agents",
    description=(
        "prepare_team_agent→security_officer_agent→prompt_engineer_agent→"
        "reviewer_agent→pm_final_report_agent の順番で実行する。"
    ),
    sub_agents=[
        prepare_team_agent,
        security_officer_agent,
        prompt_engineer_agent,
        reviewer_agent,
        pm_final_report_agent,
    ],
)


pm_agent = Agent(
    name="pm_agent",
    model=MODEL,
    instruction=pm_instruction,
    description=(
        "docs/system_dev/ の設計書に沿ったプログラムを作成するPMエージェントです。"
        "要件が固まり次第、member_agents に指示を出して作業を開始させてください。"
        "最終成果物ができたら、ユーザーに納品報告してください。"
    ),
    sub_agents=[member_agents]
)

root_agent = SequentialAgent(
    name="agent_4_agent",
    description="設計書（docs/system_dev）をINPUTにプログラムを作成し、OUTPUT_PROJECT_ROOTに出力。",
    sub_agents=[pm_agent],
)
