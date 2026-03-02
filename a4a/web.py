import os
import sys
import importlib
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn

import google.genai as genai
from google.genai import types as genai_types

from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService

from .discovery import discover_agents

STATIC_DIR = Path(__file__).parent / "static"

app = FastAPI()
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

_session_service = InMemorySessionService()
_sub_agents_cache: dict | None = None

APP_NAME = "a4a_web_ui"
USER_ID  = "web_user"
MODEL = os.environ.get("MODEL", "gemini-3-flash-preview")


def _get_sub_agents() -> dict:
    """サブエージェントをローカルにロードしてキャッシュする。"""
    global _sub_agents_cache
    if _sub_agents_cache is not None:
        return _sub_agents_cache

    root_dir = Path.cwd()
    if str(root_dir) not in sys.path:
        sys.path.insert(0, str(root_dir))

    configs = discover_agents(root_dir)
    agents = {}
    for cfg in configs:
        try:
            mod = importlib.import_module(cfg.name)
            agent = getattr(mod, "root_agent", None)
            if agent is not None:
                agents[agent.name] = agent
        except Exception as e:
            print(f"Warning: could not load '{cfg.name}': {e}")

    _sub_agents_cache = agents
    return agents


async def _route_query(query: str, sub_agents: dict) -> str:
    """Gemini に直接問い合わせてルーティング先のエージェント名を取得する。"""
    agent_list = "\n".join(
        f"- {name}: {a.description}" for name, a in sub_agents.items()
    )
    prompt = (
        "以下のエージェントリストから、ユーザーの質問に最適なエージェントを一つ選んでください。\n"
        "エージェント名のみを返してください（他のテキスト不要）。\n\n"
        f"エージェント:\n{agent_list}\n\n"
        f"ユーザーの質問: {query}"
    )

    client = genai.Client()
    resp = await client.aio.models.generate_content(model=MODEL, contents=prompt)
    name = resp.text.strip().strip('"').strip("'")

    if name in sub_agents:
        return name
    # fuzzy fallback
    for n in sub_agents:
        if n.lower() in name.lower() or name.lower() in n.lower():
            return n
    return next(iter(sub_agents))


class QueryRequest(BaseModel):
    query: str
    session_id: str = ""  # ブラウザが生成・保持するセッションID


def _echo_activity_to_terminal(message: str) -> None:
    """UI に送る作業メトリクスを Web UI 起動ターミナルにも同時表示する。"""
    if not message.strip():
        return
    print(message.strip(), flush=True)
    sys.stdout.flush()


async def stream_agent_response(query: str, session_id: str):
    sub_agents = _get_sub_agents()

    # コーディネーターがルーティング中
    yield f"data: [AGENT:coordinator_agent]\n\n"

    target_name = await _route_query(query, sub_agents)
    yield f"data: [AGENT:{target_name}]\n\n"
    _echo_activity_to_terminal(f"[ルーティング] → {target_name}")
    # リアルタイム可視化: 処理開始を UI とターミナルに表示
    _msg_start = f"[作業中] {target_name}: リクエストを処理しています..."
    yield f"data: \n{_msg_start}\n\n"
    _echo_activity_to_terminal(_msg_start)

    target_agent = sub_agents[target_name]

    # サブエージェントごとに独立したセッションで会話を継続
    agent_session_id = f"{target_name}__{session_id}"
    existing = await _session_service.get_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=agent_session_id
    )
    if existing is None:
        await _session_service.create_session(
            app_name=APP_NAME, user_id=USER_ID, session_id=agent_session_id
        )

    # ADK Runner は google.genai.types.Content を期待する（vertexai ではない）
    new_message = genai_types.Content(role="user", parts=[genai_types.Part.from_text(text=query)])

    # 作業メトリクス・作業報告用（ツール名→表示ラベルのマッピング）
    _TOOL_LABELS = {
        "write_design_doc": "設計成果物作成",
        "write_design_doc_tool": "設計成果物作成",
    }

    def _tool_display_name(call) -> str:
        name = getattr(call, "name", None) or str(call)
        args = getattr(call, "args", None)
        if args is None:
            args = {}
        if hasattr(args, "get"):
            doc_type = args.get("doc_type")
        else:
            doc_type = getattr(args, "doc_type", None)
        if doc_type == "er_diagram":
            return "ER図作成"
        if doc_type == "flow_diagram":
            return "フロー図作成"
        if doc_type == "screen_definition":
            return "画面項目定義書作成"
        if doc_type == "screen_transition":
            return "画面遷移図作成"
        if doc_type == "user_manual":
            return "ユーザーマニュアル作成"
        return _TOOL_LABELS.get(name, name)

    activity_items: list[str] = []
    had_text_response = False
    emitted_thinking = False  # 「応答を生成しています」を1回だけ

    try:
        async with Runner(
            app_name=APP_NAME,
            agent=target_agent,
            session_service=_session_service,
        ) as runner:
            async for event in runner.run_async(
                user_id=USER_ID,
                session_id=agent_session_id,
                new_message=new_message,
            ):
                # ツール呼び出し・結果を検出して作業メトリクスに追加
                get_fc = getattr(event, "get_function_calls", None)
                get_fr = getattr(event, "get_function_responses", None)
                if get_fc and callable(get_fc):
                    for call in get_fc() or []:
                        label = _tool_display_name(call)
                        activity_items.append(label)
                        _msg_tool = f"[作業中] {target_name}: {label}"
                        yield f"data: \n{_msg_tool}\n\n"
                        _echo_activity_to_terminal(_msg_tool)
                if get_fr and callable(get_fr):
                    for resp in get_fr() or []:
                        name = getattr(resp, "name", None) or "ツール"
                        if name not in _TOOL_LABELS and not any(name in s for s in activity_items):
                            activity_items.append(f"{name}完了")

                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text:
                            had_text_response = True
                            # 初回テキスト到達時に「応答を生成しています」を1回だけ表示（ツール未使用時も可視化）
                            if not emitted_thinking and not activity_items:
                                emitted_thinking = True
                                _msg_think = f"[作業中] {target_name}: 応答を生成しています..."
                                yield f"data: \n{_msg_think}\n\n"
                                _echo_activity_to_terminal(_msg_think)
                            for line in part.text.splitlines(keepends=True):
                                yield f"data: {line.rstrip(chr(10))}\n\n"
    except Exception as e:
        yield f"data: [ERROR] {e}\n\n"
    finally:
        # テキスト応答があった場合は報告に「応答生成」を1回だけ追加
        if had_text_response and "応答生成" not in activity_items:
            activity_items.append("応答生成")
        summary = ", ".join(activity_items) if activity_items else "応答"
        _msg_final = f"[エージェント活動] {target_name}: {summary}"
        yield f"data: \n\n---\n{_msg_final}\n\n"
        _echo_activity_to_terminal(_msg_final)
        yield "data: [DONE]\n\n"


@app.get("/", response_class=HTMLResponse)
async def root():
    return HTMLResponse((STATIC_DIR / "index.html").read_text(encoding="utf-8"))


@app.post("/query")
async def query(req: QueryRequest):
    return StreamingResponse(
        stream_agent_response(req.query, req.session_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


if __name__ == "__main__":
    PORT = int(os.getenv("WEB_PORT", 8888))
    print(f"\n  Web UI ready → http://localhost:{PORT}\n")
    uvicorn.run(app, host="0.0.0.0", port=PORT)
