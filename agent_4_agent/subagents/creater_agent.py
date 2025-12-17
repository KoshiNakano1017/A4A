from google.adk.agents.llm_agent import Agent
from ..tools import create_agent_files_tool, edit_agent_file_tool, get_agent_file_tool
import os
from dotenv import load_dotenv
load_dotenv()
MODEL = os.environ.get("MODEL", "gemini-2.5-flash")

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

creater_agent  = Agent(
    name="creater_agent",
    model=MODEL,
    instruction=creater_instruction,
    tools=[create_agent_files_tool]
)
