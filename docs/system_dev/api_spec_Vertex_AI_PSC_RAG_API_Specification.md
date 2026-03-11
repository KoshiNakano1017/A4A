# API仕様書：Vertex AI PSC RAG & API連携基盤

## 用語定義
- **PSC**: Private Service Connect。

## 1. 認証・認可
- **認証**: Google Identity Platform (OAuth 2.0 / OpenID Connect)
- **認可**: HTTP ヘッダーに `Authorization: Bearer <ID_TOKEN>` を付与。
- **部署制限**: API 内部でトークンからユーザーの `department_id` を抽出し、検索/操作時に強制フィルタを適用する。

## 2. 制限事項
- **リクエストサイズ**: 最大 10MB
- **タイムアウト**:
    - 検索・生成: 30s
- **性能目標 (SLO)**:
    - RAG検索・生成レスポンス: 5.0s 以内 (p95)
- **レート制限**: 100 requests / minute / user

## 3. エラー形式とステータスコード
共通エラー形式: JSON (`{ "error": { "code": 4xx/5xx, "message": "...", "request_id": "..." } }`)

| コード | 内容 | 発生理由 |
| :--- | :--- | :--- |
| 400 | Bad Request | 入力値（正規表現等）の不正 |
| 401 | Unauthorized | 無効なトークン |
| 403 | Forbidden | 他部署へのアクセス、または権限不足 |
| 404 | Not Found | リソースが存在しない |
| 429 | Too Many Requests | ユーザーまたは Vertex AI Search のクォータ超過 |
| 500 | Internal Server Error | サーバー内部エラー |

## 4. エンドポイント一覧

| メソッド | パス | 説明 | 認可 |
| :--- | :--- | :--- | :--- |
| POST | `/v1/ask` | 自然言語による質問とRAG回答の生成 | 一般ユーザー以上 |
| GET | `/v1/documents` | 自身が所属する部署のドキュメント一覧取得 | 一般ユーザー以上 |
| POST | `/v1/documents/upload` | ドキュメントのアップロードとインデックス登録 | 管理者 |
| POST | `/v1/integration/transform` | データ整形（Application Integration 呼び出し） | システム管理者 |

## 5. エンドポイント詳細

### 5.1 POST /v1/ask
- **Request Body**:
  ```json
  {
    "query": "2024年度の予算編成方針は？", // 最大 500文字
    "conversation_id": "conv-12345"
  }
  ```

### 5.2 POST /v1/documents/upload
- **Request Body (Multipart)**:
  - `file`: バイナリデータ (PDF, DOCX, TXT / 最大 10MB)
  - `metadata`:
    ```json
    {
      "department_id": "sales", // ^[a-zA-Z0-9_]{1,64}$
      "category": "guideline",   // ^[a-zA-Z0-9_]{1,64}$
      "data_store_id": "ds-123"  // ^[a-z0-9]([a-z0-9-_]{0,61}[a-z0-9])?$
    }
    ```

## 6. 監査ログ
- **記録項目**: タイムスタンプ, ユーザーID, `department_id`, メソッド, パス, ステータスコード, 検索キーワード（匿名化検討）, 実行時間。
- **保存先**: Cloud Logging
