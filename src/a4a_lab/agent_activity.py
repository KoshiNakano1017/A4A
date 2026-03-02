"""
各エージェントのターミナルに「依頼受信」「処理中」「応答送信」などを表示するための
ミドルウェアと起動ヘルパー。
"""
import os
import sys
from typing import Callable, Awaitable

from google.adk.a2a.utils.agent_to_a2a import to_a2a
import uvicorn

# ASGI types (scope, receive, send)
Scope = dict
Receive = Callable[[], Awaitable[dict]]
Send = Callable[[dict], Awaitable[None]]


def _log(agent_name: str, message: str) -> None:
    """エージェント名付きで標準出力に即時表示（フラッシュする）。"""
    line = f"[{agent_name}] {message}"
    print(line, flush=True)
    sys.stdout.flush()


class ActivityLogMiddleware:
    """リクエスト開始・応答開始をターミナルに表示する ASGI ミドルウェア。"""

    def __init__(self, app: Callable, agent_name: str):
        self.app = app
        self.agent_name = agent_name

    async def __call__(
        self,
        scope: Scope,
        receive: Receive,
        send: Send,
    ) -> None:
        if scope.get("type") != "http":
            await self.app(scope, receive, send)
            return

        _log(self.agent_name, "依頼を受信、処理中...")

        response_started = [False]

        async def wrapped_send(message: dict) -> None:
            if not response_started[0] and message.get("type") == "http.response.start":
                response_started[0] = True
                _log(self.agent_name, "応答送信開始")
            await send(message)

        await self.app(scope, receive, wrapped_send)

        if not response_started[0]:
            _log(self.agent_name, "処理完了")


def add_activity_middleware(app: Callable, agent_name: str) -> Callable:
    """ASGI アプリに活動ログ用ミドルウェアをかける。"""
    return ActivityLogMiddleware(app, agent_name)


def run_a2a_with_activity(root_agent) -> None:
    """
    指定した root_agent を A2A として起動し、依頼受信・応答送信をターミナルに表示する。
    各エージェントの a2a_agent.py から呼ぶ想定。
    """
    port = int(os.environ.get("PORT", 8001))
    app = to_a2a(root_agent, port=port)
    app = add_activity_middleware(app, root_agent.name)
    uvicorn.run(app, host="0.0.0.0", port=port)
