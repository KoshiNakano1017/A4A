# エージェントのリアルタイム動作確認手順

追加したエージェント（セキュリティ・オフィサー、プロンプト・エンジニア等）が**正しく動いているか**を、起動〜応答までリアルタイムで確認する手順です。

---

## 前提

- プロジェクトルートで `uv sync` 済み
- `.env` に `GEMINI_API_KEY` を設定済み
- 詳細なモニタリング方法は [agent_monitoring.md](agent_monitoring.md)、全体の動作確認は [verification_procedure.md](verification_procedure.md) を参照

---

## 手順 1: ログ付きで一括起動（推奨）

**ターミナル1** でプロジェクトルートから:

```bash
make run-verbose
```

Windows で `make` が使えない場合:

```powershell
python -m a4a.run_all --verbose
```

**「Python was not found」と出る場合**（uv で環境構築しているとき）:

```powershell
uv run python -m a4a.run_all --verbose
```

### 確認ポイント（起動直後）

1. **「Discovering agents...」** の直後に、検出されたエージェントが **Started ○○ on port ○○○○** で列挙されること。
2. 一覧に **`security_officer_agent`** と **`prompt_engineer_agent`** が含まれていること（並びは環境により異なります）。
3. 最後に **「Started coordinator_agent on port 8000」** が出ること。
4. **「Process ... exited with code 1」** や Python のトレースバックが出ていないこと。

例:

```
Discovering agents...
Started architect_agent on port 8001 (verbose)
Started engineer_agent on port 8002 (verbose)
...
Started security_officer_agent on port 8XXX (verbose)
Started prompt_engineer_agent on port 8XXX (verbose)
...
Started coordinator_agent on port 8000 (verbose)

--- 各エージェントのログは [エージェント名:ポート] プレフィックス付きで表示されます。Ctrl+C で終了。---

[architect_agent:8001] INFO:     Uvicorn running on http://0.0.0.0:8001
...
```

- ログが流れ続けていれば、各エージェントは起動済みです。**リアルタイムでリクエストがどのエージェントに飛んだか**は、`[エージェント名:ポート]` の行で判別できます。

---

## 手順 2: Coordinator 経由で応答確認

**ターミナル2** を開き、プロジェクトルートで:

```bash
make query q="こんにちは。あなたの役割を一言で教えてください"
```

Windows の場合:

```powershell
python -m a4a.a2a_query "こんにちは。あなたの役割を一言で教えてください" --port 8000
```

### 確認ポイント

- エラーにならず、Coordinator（PM）からの応答が返ること。
- **ターミナル1** に `[coordinator_agent:8000]` や、ルーティング先のサブエージェントのプレフィックス付きログ（例: `POST /a2a/... 200`）がリアルタイムで出ること。

---

## 手順 3: 特定エージェントの直接確認（任意）

`make run-verbose` の起動ログで、**security_officer_agent** と **prompt_engineer_agent** のポート番号を確認します（例: 8005 と 8006）。

**セキュリティ・オフィサー** に直接クエリ（ポートは実際の番号に置き換え）:

```bash
python -m a4a.a2a_query "このコードを脆弱性の観点でチェックして: print(user_input)" --port 8005
```

**プロンプト・エンジニア** に直接クエリ:

```bash
python -m a4a.a2a_query "レビューエージェントの instruction を、指摘をより具体的にする方向で改善案を出して" --port 8006
```

### 確認ポイント

- 該当エージェントからエラーではなく応答テキストが返ること。
- **ターミナル1** に、そのエージェントの `[エージェント名:ポート]` でリクエストログがリアルタイムで出ること。

---

## 手順 4: Web UI で「誰が応答したか」を確認（任意）

**ADK Web** および **A4A Web UI** の詳しい手順は [adk_web_verification.md](adk_web_verification.md) を参照。

**A4A Web UI** を使う場合、**ターミナル2** で:

```bash
make ui
```

または `uv run python -m a4a.web`。ブラウザで http://localhost:8888 を開き、クエリを送信します。

### 確認ポイント

- ストリーミング応答の先頭に **`[AGENT:○○]`** が表示され、どのエージェントが応答したかが分かること。
- セキュリティ・オフィサーやプロンプト・エンジニアにルーティングするようなクエリを送ると、該当エージェント名が表示される場合があります（Coordinator のルーティング方針に依存）。

---

## チェックリスト（リアルタイム確認）

| 確認項目 | 方法 | 期待結果 |
|----------|------|----------|
| 全エージェントが検出されている | `make run-verbose` の起動ログ | `security_officer_agent` / `prompt_engineer_agent` が Started 一覧に含まれる |
| 起動後も落ちていない | ターミナル1のログ | 途中で Process exited やトレースバックが出ない |
| Coordinator が応答する | 手順2のクエリ | 200 で応答テキストが返る |
| サブエージェントにリクエストが届く | ターミナル1のプレフィックス付きログ | クエリ送信時に該当 `[エージェント:ポート]` のログが増える |
| 個別エージェントが応答する | 手順3の直接クエリ | 該当エージェントから応答が返り、ターミナル1にそのエージェントのログが出る |

---

## 終了

- 起動した **ターミナル1** で **Ctrl+C** を押すと、`run_all` が全エージェントを停止します。
- プロセスが残る場合は [troubleshooting.md](troubleshooting.md) の「ポート競合・ゾンビプロセス」を参照。
