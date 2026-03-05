from google.adk.agents.llm_agent import Agent
from google.adk.agents import SequentialAgent
import os
from dotenv import load_dotenv
from .subagents import (
    planning_agent,
    planning_b_agent,
    investigation_agent,
    investigation_validation_agent,
    investigation_review_validation_agent,
    architect_agent,
    ops_prompt_engineer_agent,
    architect_review_agent,
)
from architect_agent.tools.design_docs_tool import write_design_doc_tool

load_dotenv()
MODEL = os.environ.get("MODEL", "gemini-3-flash-preview")

# 企画フェーズの自律連動チェーン: 調査→企画→裏付け→レビュー→裏付け
planning_phase_agents = SequentialAgent(
    name="planning_phase_agents",
    description="調査→企画→裏付け→レビュー→裏付けの順で自律的に実行。各エージェントが作業完了後にPMへ報告する。",
    sub_agents=[
        investigation_agent,                    # 1. 調査
        planning_agent,                        # 2. 調査に基づいて企画
        investigation_validation_agent,        # 3. 企画を裏付け
        planning_b_agent,                      # 4. 企画をレビュー
        investigation_review_validation_agent, # 5. レビュー内容を裏付け
    ],
)

_name = "ops_agent"
_description = (
    "運用保守・DevOpsと上流工程のPM機能を兼ねる運用保守エージェント。"
    "企画フェーズは planning_phase_agents で自律連動し、設計・レビュー系エージェントを束ねる。"
)
_instruction = """
あなたは運用保守（運用保守改築）エージェントであり、上流工程のPMチームの司令塔です。

【企画フェーズの自律連動（ユーザー要望確認〜企画完了まで）】
1. **ユーザーの要望を確認**する。不明点があれば質問する。
2. **planning_phase_agents に依頼**し、以下の流れを自律的に実行させる：
   - 調査エージェント: ユーザー要望・背景を調査
   - 企画エージェント: 調査に基づいて企画案を作成
   - 調査エージェント: 企画案の裏付け検証
   - 企画エージェントB: 企画案を否定的立場でレビュー
   - 調査エージェント: レビュー内容の裏付け検証
3. **各サブエージェントの作業内容をPMを通してユーザーに伝える**。出力を「[調査] 〇〇」「[企画] 〇〇」「[裏付け] 〇〇」「[レビュー] 〇〇」のように区切り、誰が何をしたか分かる形で報告する。
4. **企画案をユーザーに提出**する。要約・推奨案・判断材料を分かりやすくまとめる。
5. **ユーザーが「承認」「企画完了」等と言ったら**：企画・調査の内容を統合し、**write_design_doc**（doc_type=requirements_spec）で要求仕様を作成し、docs/system_dev に格納する。その後 architect_review_agent にレビューを依頼し、Go になるまで修正を繰り返す。

【設計〜レビューの自律ループ（要求仕様確定後）】
- 要求仕様が docs/system_dev に格納されたら、そのパスを architect_agent に渡して設計を依頼する。
- architect_agent から「詳細な設計要約」と「設計ファイル一覧（docs/system_dev/... のパス群）」を受け取ったら、そのパスを使って architect_review_agent にレビューを依頼する。依頼メッセージには、対象ファイルごとに「パス: docs/system_dev/xxx.md」を明示し、read_design_doc で読み取って ER図とインフラの分離・認可モデルの整合性・API制約の準拠を検証するよう指示する。
- architect_review_agent からレビュー結果を受け取ったら、判定が「判定: 要修正」の場合は、指摘内容を要約し、該当する設計ファイルとともに architect_agent に送り「レビュー指摘を反映した設計の改訂」を依頼する。その後、architect_agent が write_design_doc で設計を更新し、新しい設計ファイル一覧を出したら、再度 architect_review_agent に同じパス（または更新後のパス）でレビューを依頼する（必要に応じて複数回繰り返してよい）。
- 判定が「判定: Go」の場合は、設計要約とレビュー結果（主要な確認ポイントと問題なしであった点）、レビュー中に行った主な修正内容を統合し、**ユーザー向けの最終設計レポート**として報告する。その際、「この時点の設計が下流工程（agent_4_agent チーム）に渡すべき正本である」ことを明示し、次ステップ（実装・テスト・デプロイ）への移行提案を行う。

【運用保守・DevOps】
- 稼働中システムのメトリクス把握、異常時LOG、対応方針の提案・承認後自動修正

【ルール】
- 各エージェントの出力をユーザーに分かりやすく伝える
- 企画承認後は必ず要求仕様を作成し、レビューを通す
"""

root_agent = Agent(
    name=_name,
    model=MODEL,
    description=_description,
    instruction=_instruction,
    sub_agents=[
        planning_phase_agents,
        architect_agent,
        ops_prompt_engineer_agent,
        architect_review_agent,
    ],
    tools=[write_design_doc_tool],
)
