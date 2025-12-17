from google.adk.agents.llm_agent import Agent
from google.adk.agents import ParallelAgent, SequentialAgent
from google.adk.tools import FunctionTool
import os
from dotenv import load_dotenv
load_dotenv()
MODEL = os.environ.get("MODEL", "gemini-2.5-flash")

# ファイル作成用のカスタムツール
def create_agent_files(agent_name: str, agent_code: str) -> str:
    """新しいエージェントのディレクトリとファイルを作成する
    agent_name: エージェント名（英小文字+_）
    agent_code: エージェントのPythonコード
    戻り値: 成功/失敗メッセージ
    """
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        agent_dir = os.path.join(base_path, agent_name)
        # エージェントディレクトリを作成
        os.makedirs(agent_dir, exist_ok=True) 
        # __init__.pyファイルを作成
        with open(os.path.join(agent_dir, "__init__.py"), "w") as f:
            f.write("from . import agent\n")
        # agent.pyファイルを作成
        with open(os.path.join(agent_dir, "agent.py"), "w") as f:
            f.write(agent_code)
        # 実行ファイルの階層にある.envファイルをコピーしてここに配置
        with open(os.path.join(script_dir, ".env"), "r") as f_src:
            env_content = f_src.read()
        with open(os.path.join(agent_dir, ".env"), "w") as f_dst:
            f_dst.write(env_content)

        return f"成功: {agent_name} を作成しました ({agent_dir})"
    except Exception as e:
        return f"エラー: {str(e)}"
    
# ファイル取得用のカスタムツール
def get_agent_file(agent_name: str, file_name: str) -> str:
    """既存のエージェントファイルを取得する
    agent_name: エージェント名（英小文字+_）
    file_name: 取得するファイル名（例: agent.py）
    戻り値: ファイル内容またはエラーメッセージ
    """
    try:
        # このファイルの2階層上のディレクトリを取得
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path = os.path.join(base_path, agent_name, file_name)
        
        if not os.path.isfile(file_path):
            return f"エラー: ファイルが存在しません ({file_path})"
        
        with open(file_path, "r") as f:
            content = f.read()
        
        return content
    except Exception as e:
        return f"エラー: {str(e)}"

# ファイル更新用のカスタムツール
def edit_agent_file(agent_name: str, file_name: str, new_code: str) -> str:
    """既存のエージェントファイルを編集する
    agent_name: エージェント名（英小文字+_）
    file_name: 編集するファイル名（例: agent.py）
    new_code: 新しいコード内容
    戻り値: 成功/失敗メッセージ
    """
    try:
        # このファイルの2階層上のディレクトリを取得
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path = os.path.join(base_path, agent_name, file_name)
        
        if not os.path.isfile(file_path):
            return f"エラー: ファイルが存在しません ({file_path})"
        
        with open(file_path, "w") as f:
            f.write(new_code)
        
        return f"成功: {file_name} を更新しました ({file_path})"
    except Exception as e:
        return f"エラー: {str(e)}"
    

create_agent_files_tool = FunctionTool(func=create_agent_files)
get_agent_file_tool = FunctionTool(func=get_agent_file)
edit_agent_file_tool = FunctionTool(func=edit_agent_file)



# --- PM（要件化＆タスク分解） ---
pm_instruction = """
あなたはPMエージェントです。
ユーザーの要望からエージェント作成の要件を明確化するのが役割です。

【手順】
1. まずユーザーの要望を確認する
2. 不明確な点があれば「合計1回だけ」質問してよい
3. 次を決定する：
   - agent_name（短く分かりやすい英小文字+_）
   - goal（目的1行）
   - research_brief（searcher/surfer 共通の調査方針。プロンプトに入れるための材料を集める）
   - creater_agentへの指示（まず動くコード優先）
4. 要件が固まったら「要件確定しました」と明示し、フォーマットに従って指示を出す
5. member_agents（prepare_team_agent → reviewer_agent）に作業を開始させる
6. reviewer_agent の完了報告を受け取ったら、あなたが最終成果物を確認し、ユーザーに「納品報告」を行う
   - get_agent_file_tool で最終 agent.py を取得して、要点を確認する
   - ユーザーへの報告には「作ったもの」「使い方」「次に調整できる点」を含める

[サブエージェント]
- prepare_team_agent: searcher/surfer/creater を並列に実行する
- reviewer_agent: prepare_team_agent の出力を反映し、生成物を改善する

[重要]
- 曖昧な箇所はよしなに決めてよい
- 要件確定後は必ず以下フォーマットで出力する：


```
# 要件確定

## agent_name:
[名前]

## goal: 
[目的]

## research_brief（searcher/surfer 共通）
- 調べたい対象:
- 何のために調べるか（instructionへどう入れるか）:
- ほしいアウトプット（コピペ可能な箇条書き）:
- 禁止事項（捏造しない等）:

## creater_agentへの指示
[作成すべきエージェントの詳細]

```

"""


# --- prepare team（並列） ---
searcher_instruction = """
あなたはリサーチ担当です。
PMエージェントが「---要件確定---」の後に出した
【research_brief（searcher/surfer 共通）】に従って調査・整理してください。

重要: ただ調べるだけでなく、最終的に生成される agent.py の _instruction に
「そのまま貼れる」材料を作ることが目的です。

出力は必ず次のMarkdown構造にしてください（コピペしやすさ重視）:

# prompt_inserts
## role_and_scope
- （役割や対象範囲として instruction に入れられる文）

## do_list
- （やること / できること）

## dont_list
- （やらないこと / 禁止事項 / 注意）

## workflow
- （進め方: 例: まず確認→整理→提案…）

## memos
- （補足：根拠や注意点。あれば）
"""

surfer_instruction = """
あなたはネットサーフィン担当です。
PMエージェントが「---要件確定---」の後に出した
【research_brief（searcher/surfer 共通）】に従う必要は全くありません。
雑学や、珍事件など面白い話題を広く調査し、要点を箇条書きで出してください。
あと、エージェントのキャラクや口調もどういう感じが良さそうかも提案してください。
オリジナルあるエージェントになるように工夫してください。

出力は必ず次のMarkdown構造にしてください（コピペしやすさ重視）:

# prompt_inserts
## interesting_points
- （面白い話題、珍事件、雑学など）

## character_suggestions
- （エージェントのキャラクや口調の提案）

## memos
- （補足：根拠や注意点。あれば）
"""

creater_instruction = """
あなたはcreater_agentです。
PMエージェントが「---要件確定---」の後に出した【creater_agentへの指示】に基づき、
生成対象エージェントをコードで作成してください。

最優先: まずは動くコードを作る（プロンプトの細部は後で改善可能）。
作業が完了したら、必ず pm_agent にやった内容を報告してください。
PMからの指示がまだない場合は待機してください。

**必ずcreate_agent_files_toolを使ってファイルを作成してください。**

create_agent_files_toolの使い方：
- agent_name: PMが決めたエージェント名（英小文字+_）
- agent_code: 以下のテンプレートを埋めた完全なPythonコード

テンプレート：
```python
from google.adk.agents.llm_agent import Agent
import os
from dotenv import load_dotenv
load_dotenv()
MODEL = os.environ.get("MODEL", "gemini-2.5-flash")
_name = "TODO"  # PMの指示から設定
_description = "TODO"  # PMの指示から設定
_instruction = \"\"\"
TODO  # PMの指示から設定
\"\"\"

root_agent = Agent(
    name=_name,
    model="gemini-2.5-flash",
    description=_description,
    instruction=_instruction,
    tools=[],
)
```

PMの指示に従って、適切な_name、_description、_instructionを設定し、
create_agent_files_toolを呼び出してファイルを作成してください。
"""

searcher_agent = Agent(name="searcher_agent", model=MODEL, instruction=searcher_instruction)
surfer_agent   = Agent(name="surfer_agent",   model=MODEL, instruction=surfer_instruction)
creater_agent  = Agent(
    name="creater_agent",
    model=MODEL,
    instruction=creater_instruction,
    tools=[create_agent_files_tool]
)

prepare_team_agent = ParallelAgent(
    name="prepare_team_agent",
    description="searcher/surfer/creater を並列に実行する。",
    sub_agents=[searcher_agent, surfer_agent, creater_agent],
)

# --- review_agent ---
reviewer_instruction = """
あなたはreviewer_agentです。
PMの要件と prepare_team_agent（searcher/surfer/creater）の出力を受け取り、最終生成物を改善してください。

目的:
- creater_agent が作った agent.py の _instruction に、
  searcher/surfer の # prompt_inserts を「自然に統合」して完成度を上げる。

[手順]
1. PMが決めたagent_name、goalを確認する
2. prepare_team_agentの出力を確認する
3. creater_agentが作成したエージェントコードをget_agent_file_toolを使って取得する
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

# --- pm_report agent ---
pm_final_report_instruction = """
あなたはpm_final_report_agentです。
member_agents の作業が終わったら、必ず最後にユーザーへ以下の形式で納品報告してください：

```
---納品---

## 作成したエージェント
- agent_name: XXX
- 目的: XXX
- 概要: XXX
- 特徴: XXX

## 生成ファイル
- XXX/agent.py
- XXX/.env

## 次に調整できる点&改善案
- XXX

```

"""

pm_final_report_agent = Agent(
    name="pm_final_report_agent",
    model=MODEL,
    instruction=pm_final_report_instruction,
)

member_agents = SequentialAgent(
    name="member_agents",
    description="prepare_team_agentとreviewer_agentとpm_final_report_agentを順番に実行する。",
    sub_agents=[prepare_team_agent, reviewer_agent, pm_final_report_agent],
)


# --- root_agent ---

pm_agent = Agent(
    name="pm_agent",
    model=MODEL,
    instruction=pm_instruction,
    description=(
        "Agentを作成するためのPMエージェントです。"
        "要件が固まり次第、member_agents（prepare_team_agent→reviewer_agent）に指示を出して作業を開始させてください。"
        "最終成果物ができたら、必ずユーザーに納品報告してください。"
    ),
    sub_agents=[member_agents]
)

root_agent = SequentialAgent(
    name="agent_4_agent",
    description="PMで要件確定→membersで作成→reviewerで改善→PMがユーザーに納品報告。",
    sub_agents=[pm_agent],
)
