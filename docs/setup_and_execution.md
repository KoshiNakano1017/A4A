# セットアップと実行

## セットアップ手順
以下ターミナルより実行します。
```bash
git clone https://github.com/KoshiNakano1017/A4A
uv sync
source .venv/bin/activate
cp agent_4_agent/.env.example agent_4_agent/.env
```

.envファイルにGEMINI_API_KEYを設定してください

GEMINI_API_KEYは、以下から取得できます。

https://aistudio.google.com/api-keys

.envファイルに、作成したプログラムの保存先を指定してください
OUTPUT_PROJECT_ROOT=格納したいPATH

## 実行手順
以下ターミナルより実行します。
ブラウザでチャットするには
・A4A 用の Web UI は ポート 8888 で動かします。
・ターミナルで uv run python -m a4a.run_all --verbose を起動したままにする。
・別のターミナルで次を実行する。
　・uv run python -m a4a.web
・ブラウザで http://localhost:8888 を開く。

ここがチャット画面で、ここにクエリを送ると Coordinator 経由でエージェントが応答します。
