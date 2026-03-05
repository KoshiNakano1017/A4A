# .env に必要な値

プロジェクトルートの `.env`、または `agent_4_agent/.env` に設定する環境変数の一覧です。

---

## 必須（ローカルでエージェントを動かす場合）

| 変数名 | 説明 | 例 |
|--------|------|-----|
| **GEMINI_API_KEY** | Gemini API キー（Google AI Studio で発行）。ADK が LLM 呼び出しに使用。 | `AIzaSy...` |
| または **GOOGLE_API_KEY** | 上記の代替。ライブラリによってはこちらを参照する。 | `AIzaSy...` |

- 取得先: https://aistudio.google.com/api-keys  
- どちらか一方を設定すればよい。ドキュメントでは `GEMINI_API_KEY` を案内していることが多い。

---

## 任意（デフォルトでよい場合は省略可）

| 変数名 | 説明 | デフォルト |
|--------|------|------------|
| **MODEL** | 各エージェントが使う LLM モデル名。 | `gemini-3-flash-preview` |
| **PORT** | Coordinator またはサブエージェントのポート。通常は `run_all` が自動で振るため指定不要。 | 8000（Coordinator） / 8001〜（サブ） |
| **WEB_PORT** | Web UI のポート。 | `8888` |
| **OUTPUT_PROJECT_ROOT** | 設計成果物の参照・出力先ルート。A4Aエージェントはこのルートの `docs/system_dev` に格納されたファイルを参照して実装する。未設定時は A4A プロジェクト内。 | 例: `C:/Users/nakano-koshi/project` → `C:\Users\nakano-koshi\project\docs\system_dev` を参照 |

---

## デプロイ・GCP 利用時のみ

`agent_4_agent` のデプロイや Vertex AI を使う場合に必要です。

| 変数名 | 説明 | 例 |
|--------|------|-----|
| **GOOGLE_GENAI_USE_VERTEXAI** | Vertex AI を使う場合は 1。 | `0`（AI Studio） / `1`（Vertex） |
| **PROJECT_ID** | GCP プロジェクト ID。 | `your-gcp-project-id` |
| **LOCATION** | Vertex AI のリージョン。 | `us-central1` |
| **STAGING_BUCKET** | デプロイ用 GCS バケット。 | `gs://your-bucket` |
| **AGENT_RESOURCE_NAME** | デプロイ済みエージェントのリソース名（クエリ用）。 | デプロイ後に得られる ID |

---

## .env の最小例（ローカル実行のみ）

```env
GEMINI_API_KEY=あなたのAPIキー
```

または（ライブラリがこちらを読む場合）:

```env
GOOGLE_API_KEY=あなたのAPIキー
```

モデルを変えたい場合:

```env
GEMINI_API_KEY=あなたのAPIキー
MODEL=gemini-3-flash-preview
```

---

## 注意

- `.env` は git にコミットしないでください（機密情報を含むため）。`.gitignore` に含めることを推奨。
- プロジェクトルートに `.env` があれば、多くのエージェントが `load_dotenv()` で読み込みます。`agent_4_agent/.env` だけにある場合は、そのディレクトリから実行する処理のみが参照します。
