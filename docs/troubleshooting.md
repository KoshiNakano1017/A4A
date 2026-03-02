# 起こりうるエラーとはまりやすいポイント

A4A およびシステム開発ツール運用で遭遇しやすいエラーと、はまりやすいポイントをまとめます。

---

## 1. 起動・ discovery まわり

### 1.1 エージェントの import 失敗（`root_agent` が取れない）

**現象**
- `make run` 時に `Warning: Could not import {module_name} to read description: ...`
- またはサブエージェント起動時に `ModuleNotFoundError` / `ImportError`

**原因**
- **`from .import root_agent` の typo**  
  `a2a_agent.py` で `from . import root_agent`（ドットの後にスペース）が正しい。  
  `from .import root_agent` だと `.import` というサブモジュールを探しにいき **ImportError** になる。
- プロジェクトルートが `sys.path` に入っておらず、`python -m a4a.run_all` を**ルート以外のカレントディレクトリ**で実行している。

**対処**
- 各エージェントの `a2a_agent.py` を `from . import root_agent` に統一する。
- 必ず **プロジェクトルートで** `make run` または `python -m a4a.run_all` を実行する。

---

### 1.2 ポート番号のずれ・競合

**現象**
- Coordinator (8000) からサブエージェントに接続できない。
- `Address already in use` でプロセスが起動しない。

**原因**
- **discovery の走査順は保証されない**（`Path.iterdir()` の順序に依存）。  
  実行ごとに「どのエージェントが 8001 / 8002 / … か」が変わりうる。
- 前回の `make run` や手動起動のプロセスが残っており、同じポートを使っている。

**対処**
- クライアントは **必ず 8000（PM/Coordinator）にだけ** 話しかける。サブエージェントのポートは直接前提にしない。
- 起動前に `make clean`（または手動で `pkill -f a2a_agent` / `a4a.agent`）で残りプロセスを落とす。  
  **Windows** では `pkill` がないため、タスクマネージャーや `taskkill /F /IM python.exe` で整理する。

---

### 1.3 Windows で `make query` / `make clean` が動かない

**現象**
- `make query q='Hello'` でエラーになる。
- `make clean` で「pkill がない」などと出る。

**原因**
- Makefile が **bash 前提**（`[ -z "$(q)" ]`、`pkill`）のため、Windows の `make`（例: MinGW）や別シェルではそのまま動かない場合がある。

**対処**
- クエリは直接実行する:
  ```bash
  python -m a4a.a2a_query "あなたのクエリ" --port 8000
  ```
- プロセス終了は手動で行う（タスクマネージャー、または `taskkill /F /IM python.exe` で該当プロセスのみ終了）。

---

## 2. アーキテクトエージェント・設計成果物

### 2.1 設計ドキュメントが保存されない / パスエラー

**現象**
- `write_design_doc` を呼んだがファイルが出てこない。
- `PermissionError` や `FileNotFoundError` が出る。

**原因**
- **プロジェクトルートの想定が違う**  
  `design_docs_tool.py` は `Path(__file__).resolve().parent.parent.parent` を「プロジェクトルート」としている。  
  つまり `architect_agent/tools/design_docs_tool.py` の 3 階層上。  
  リポジトリ構造を変えたり、別ディレクトリから `-m` で実行したりするとずれる。
- **書き込み権限**がない（`docs/system_dev/` やその親が読取専用など）。

**対処**
- 必ず **プロジェクトルートを cwd にして** エージェントを起動する（`run_all` は cwd を変えていないので、`make run` をルートで実行していれば通常は一致する）。
- `docs/system_dev/` を事前に作成し、書き込み可能であることを確認する。

---

### 2.2 `doc_type` を間違える

**現象**
- ツールが `success: False` を返し、`不明な doc_type: xxx` とメッセージが返る。

**原因**
- `write_design_doc` の `doc_type` に、定義外の文字列を渡している。

**対処**
- 使用可能な値だけ使う:  
  `flow_diagram` / `er_diagram` / `user_manual` / `screen_definition` / `screen_transition`  
  実装は `architect_agent/tools/design_docs_tool.py` の `DOC_TYPE_MAP` を参照。

---

## 3. 環境変数・API

### 3.1 GEMINI_API_KEY がない / 無効

**現象**
- エージェントが応答しない、または ADK/Vertex 周りで認証エラーになる。

**原因**
- `.env` が無い、または `GEMINI_API_KEY`（あるいは Vertex 用の認証）が未設定・無効。

**対処**
- プロジェクトまたは `agent_4_agent` の `.env.example` をコピーして `.env` を作成し、  
  [Google AI Studio](https://aistudio.google.com/api-keys) などで取得したキーを設定する。
- サブプロセスは `run_all` で `os.environ.copy()` を渡しているため、**起動したシェルで export した環境変数**は子プロセスにも渡る。  
  `.env` を読むのは各エージェントの `agent.py` 内 `load_dotenv()` なので、カレントディレクトリがルートであればルートの `.env` が読まれる。

---

### 3.2 `a4a.web` 起動時に vertexai で落ちる / 読み込みが遅い

**現象**
- `uv run python -m a4a.web` 実行時に、`from vertexai.generative_models import Content, Part` のあとでエラーになる、またはインポートが非常に遅い。

**原因（過去の実装）**
- Web UI と `a2a_query` で、ADK の `Runner.run_async(new_message=...)` に渡す「ユーザーメッセージ」を組み立てるために、`vertexai.generative_models.Content` と `Part` を使っていました。
- `vertexai` は `google.cloud.aiplatform` 一式を読み込むため重く、GCP 認証が必要な環境では負荷やエラーの原因になります。

**対処（現在の実装）**
- ADK の `Runner.run_async` が期待しているのは **`google.genai.types.Content`** です。実装を `google.genai.types` の `Content` / `Part` に変更してあり、**vertexai の import は不要**です。
- まだ `vertexai` を参照している箇所があれば、`google.genai.types` に置き換えてください。

---

### 3.3 MODEL の指定違い

**現象**
- 使いたいモデルと違うモデルが動く、または「モデルがない」と出る。

**原因**
- 各 `agent.py` で `MODEL = os.environ.get("MODEL", "gemini-3-flash-preview")` のようにデフォルトを参照している。  
  環境変数 `MODEL` が未設定ならデフォルトになる。

**対処**
- 必要なら `.env` や起動前に `export MODEL=...` で `MODEL` を設定する。

---

## 4. 複数エージェント・サブプロセス

### 4.1 サブエージェントが先に落ちる

**現象**
- `make run` 直後に「Process ... exited with code 1」などと出て、該当エージェントだけ終了する。

**原因**
- そのエージェントの **import 時エラー**（上記 1.1 の typo、依存モジュール不足、`root_agent` 未定義など）。
- **ポート競合**で uvicorn が起動に失敗している。

**対処**
- 該当エージェントを単体で起動してスタックトレースを確認する:
  ```bash
  cd プロジェクトルート
  PORT=8001 python -m architect_agent.a2a_agent
  ```
- エラーメッセージに従って import / 依存 / ポートを修正する。

---

### 4.2 Coordinator がサブエージェントを「見つけられない」

**現象**
- 8000 に話しかけると「その機能は別エージェントに任せる」と言うが、実際には依頼先が動いていない、または別ポートで動いている。

**原因**
- discovery で得た **AgentConfig の url（agent-card の URL）** は `http://127.0.0.1:{port}/.well-known/agent-card.json`。  
  ポートが前回起動時と変わっていると、Coordinator が持つ URL と実プロセスのポートが一致しない。
- サブエージェントの起動が遅く、Coordinator が先に agent-card を取得しにいって失敗している（レースコンディション）。

**対処**
- 起動後、少し待ってから 8000 にクエリを送る。
- 必要なら `run_all` 側でサブエージェント起動後に一定時間 `time.sleep` を入れるなど、起動順序・待機を調整する。

---

## 5. はまりやすいポイント一覧（チェックリスト）

| 項目 | 内容 |
|------|------|
| **cwd** | 常に **プロジェクトルート** で `make run` / `python -m a4a.run_all` を実行する。 |
| **import の typo** | `a2a_agent.py` は `from . import root_agent`（ドットの後にスペース）。 |
| **ポート** | ユーザーは 8000 だけを前提にする。8001 以降は discovery 順で変わりうる。 |
| **ゾンビプロセス** | 起動前に前回の Python プロセスを終了させる（`make clean` または手動）。 |
| **Windows** | `make query` / `make clean` は bash 前提のため、必要なら `python -m a4a.a2a_query` や手動 kill で代替。 |
| **設計成果物のパス** | アーキテクトの保存先は「実行時の cwd = プロジェクトルート」を前提にしている。 |
| **.env** | ルートまたはエージェント配下に `.env` を置き、`GEMINI_API_KEY` 等を設定する。 |
| **エージェント追加時** | 新規エージェントは **`a2a_agent.py` を必ず置く**。`__init__.py` で `root_agent` を export する。 |

---

## 6. import の typo について

**過去の事象**: 一部の `a2a_agent.py` で `from .import root_agent`（ドットの後スペースなし）になっており、環境によっては **ImportError** の原因になっていました。  
本ドキュメント整備時に `from . import root_agent` へ一括修正済みです。  
新規エージェントを追加するときは、`a2a_agent.py` で **`from . import root_agent`** と書くようにしてください。
