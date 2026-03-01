# セットアップと実行

## セットアップ手順
以下ターミナルより実行します。
```bash
git clone https://github.com/tyukei/A4A.git
uv sync
source .venv/bin/activate
cp agent_4_agent/.env.example agent_4_agent/.env
```

.envファイルにGEMINI_API_KEYを設定してください

GEMINI_API_KEYは、以下から取得できます。

https://aistudio.google.com/api-keys

## 実行手順
以下ターミナルより実行します。
```bash
adk web
```
open http://127.0.0.1:8000

チャットで作りたいエージェントを入力します

例：沖縄そばエージェントを作成したい。

![alt text](../assets/image.png)

質問に答えていきます

![alt text](../assets/image-1.png)

最終報告がされること確認します

![alt text](../assets/image-2.png)

ブラウザをリフレッシュして、左上のエージェントを切り替えます。
作成成功していれば、新しいエージェントが選択できるようになっています。

![alt text](../assets/image-3.png)

新しく作成したエージェントに質問をします。
例：おすすめのお店を教えて

![alt text](../assets/image-4.png)

---

## ブラウザでチャット（A4A Web UI）

ブラウザからチャット形式でエージェントにクエリを送り、Coordinator 経由で応答を確認できます。以下、ターミナルより実行します。

### 手順（2 本のターミナルで実行）

**ターミナル 1** — 全エージェントと Coordinator を起動したままにします。

```bash
uv run python -m a4a.run_all --verbose
```

**ターミナル 2** — Web UI を起動します。

```bash
uv run python -m a4a.web
```

**ブラウザ**で **http://localhost:8888** を開きます。

ここがチャット画面です。クエリを送ると Coordinator 経由でエージェントが応答します。

### 補足

- リアルタイムストリーミングで回答を表示
- どのサブエージェントが応答したかバッジ（`[AGENT:名前]`）で確認可能
- マークダウン形式でレンダリング
- 同一タブ内で会話が継続（サブエージェントごとにセッション管理）

**Windows で `make` を使う場合**  
`make run-verbose`（ターミナル 1）と `make ui`（ターミナル 2）でも同じ動作になります。
