# 動作確認手順

A4A およびシステム開発ツールの動作を確認する手順です。

- **リアルタイムでログを見ながら確認したい場合** → [realtime_verification.md](realtime_verification.md) を参照。

---

## 1. 前提条件

- Python 3.12+
- プロジェクトルートで `uv sync` 済み
- `.env` に `GEMINI_API_KEY` を設定済み（ルートまたは `agent_4_agent/.env` をコピーして設定）

```bash
# 例: ルートで
cp agent_4_agent/.env.example .env
# .env を編集して GEMINI_API_KEY を設定
```

---

## 2. 全エージェントの起動確認

### 2.1 通常起動

```bash
# プロジェクトルートで
make run
```

- 「Discovering agents...」の後に「Started ○○ on port ○○○○」が複数行出ること
- 最後に「Started coordinator_agent on port 8000」が出ること
- 途中で「Process ... exited with code 1」が出ないこと

### 2.2 ログ付き起動（推奨）

```bash
make run-verbose
```

- 各エージェントの uvicorn ログが `[エージェント名:ポート]` 付きで流れること
- 起動完了後、どのポートにどのエージェントが立っているか確認できること

---

## 3. Coordinator（PM）へのクエリ確認

別ターミナルで、プロジェクトルートから:

```bash
make query q="こんにちは。あなたの役割を一言で教えてください"
```

- エラーにならず、PM（コーディネーター）からの応答が返ること

**Windows の場合**（`make query` が使えないとき）:

```bash
python -m a4a.a2a_query "こんにちは" --port 8000
```

---

## 4. Web UI の確認

- **ADK Web** または **A4A Web UI** でブラウザから動作確認する手順は [adk_web_verification.md](adk_web_verification.md) を参照。

**A4A Web UI（Coordinator 経由）** の場合:

```bash
make ui
```

- 先に `make run`（または `uv run python -m a4a.run_all`）で全エージェントを起動しておく
- ブラウザで http://localhost:8888 を開く
- クエリを入力して送信すると、ストリーミングで応答が返ること
- 応答先頭に `[AGENT:○○]` が表示され、どのエージェントが応答したか分かること

---

## 5. システム開発ツールの確認（PM・企画・設計）

以下のクエリで、PM が企画やアーキテクトを利用する流れを確認する。

### 5.1 ふわっとした要望の具体化（企画相談）

```bash
make query q="業務を効率化したい"
```

- PM が要望を「ふわっとしている」と判断し、企画と相談するか、ユーザーに質問して具体化しようとすること
- いきなり設計・実装に入らず、質問や整理が行われること

### 5.2 設計の依頼（具体化後）

```bash
make query q="会員登録画面の画面項目定義書と画面遷移図を設計して。成果物は docs に保存して"
```

- PM が architect_agent に依頼すること
- `docs/system_dev/` に該当する Markdown が作成されること

### 5.3 設計成果物の確認

```bash
# プロジェクトルートで
ls docs/system_dev/
# または Windows
dir docs\system_dev
```

- アーキテクトが生成したファイル（flow_diagram_*.md, screen_item_definition_*.md 等）が存在すること

---

## 6. 個別エージェントの直接確認（任意）

特定エージェントのポートは `make run-verbose` の起動ログで確認する。例: 8001 が architect_agent の場合:

```bash
python -m a4a.a2a_query "画面遷移図のフォーマットを教えて" --port 8001
```

- 該当エージェントから応答が返ること

---

## 7. 終了とクリーンアップ

- 起動したターミナルで **Ctrl+C** を押すと、run_all が全プロセスを停止する
- プロセスが残る場合は `make clean`（Linux/macOS）。Windows の場合はタスクマネージャーまたは `taskkill` で該当 Python プロセスを終了する

---

## 8. 確認結果の記録

動作確認の結果は、必要に応じて **`docs/test_specs/`** にテスト仕様書・結果メモとして格納する。  
テスト仕様書の格納ルールは `docs/test_specs/README.md` を参照。
