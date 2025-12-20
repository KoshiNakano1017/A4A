import os
import uvicorn
from dotenv import load_dotenv
from google.adk.agents.llm_agent import LlmAgent
from google.adk.a2a.utils.agent_to_a2a import to_a2a
import yaml
from pathlib import Path
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
load_dotenv() # .envファイルがあれば読み込む


def load_remote_agents(config_name: str = "agents.yaml"):
    """
    YAMLファイルからエージェント設定を読み込み、RemoteA2aAgentのリストを返します。
    ファイルはこのスクリプトと同じディレクトリにあると想定します。
    """
    current_dir = Path(__file__).parent
    path = current_dir / config_name
    
    if not path.exists():
        print(f"Warning: Configuration file not found at {path}")
        return []

    with open(path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    agents = []
    for agent_cfg in config.get("agents", []):
        # print(f"Loading agent: {agent_cfg['name']} at {agent_cfg['url']}")
        agent = RemoteA2aAgent(
            name=agent_cfg["name"],
            agent_card=agent_cfg["url"],
            description=agent_cfg.get("description", "")
        )
        agents.append(agent)
    
    return agents


def create_coordinator_agent():
    # 同一パッケージ（ディレクトリ）内の utils から読み込む
    remote_agents = load_remote_agents()

    # 親（コーディネーター）エージェントを定義
    coordinator = LlmAgent(
        name="coordinator_agent",
        instruction=f"""
        あなたはAgentコーディネーターです。
        以下のリストにあるAgentを活用して、ユーザーの依頼に応えてください。
        それぞれのAgentの機能は以下の通りです。
        {remote_agents}
        """,
        model="gemini-2.5-flash",
        sub_agents=remote_agents
    )
    
    return coordinator

if __name__ == "__main__":
    PORT = int(os.getenv("PORT", 8000))
    app = to_a2a(create_coordinator_agent(), port=PORT)
    uvicorn.run(app, host="0.0.0.0", port=PORT)
