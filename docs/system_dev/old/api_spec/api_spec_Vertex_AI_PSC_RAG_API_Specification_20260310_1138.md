# API仕様書：Vertex AI PSC RAG & API連携基盤

## 1. 認証・認可
- **認証**: Google Identity Platform (OAuth 2.0 / OpenID Connect)
- **認可**: HTTP ヘッダーに `Authorization: Bearer <ID_TOKEN>` を付与。
- **部署制限**: API 内部でトークンからユーザーの `department_id` を抽出し、検索/操作時に強制フィルタを適用する。
- **共通エラー形式**: JSON (`{ "error": { "code": 4xx/5xx, "message": "...", "request_id": "..." } }`)

## 2. 制限事項
- **リクエストサイズ**: 最大 10MB
- **タイムアウト**:
    - 検索: 10s
    - 生成: 30s
- **レート制限**: 100 requests / minute / user

## 3. エンドポイント一覧

| メソッド | パス | 説明 | 認可 |
| :--- | :--- | :--- | :--- |
| POST | `/v1/ask` | 自然言語による質問とRAG回答の生成 | 一般ユーザー以上 |
| GET | `/v1/documents` | 自身が所属する部署のドキュメント一覧取得 | 一般ユーザー以上 |
| POST | `/v1/documents/upload` | ドキュメントのアップロードとインデックス登録 | 管理者 |
| POST | `/v1/integration/transform` | データ整形（Application Integration 呼び出し） | システム管理者 |

## 4. エンドポイント詳細

### 4.1 POST /v1/ask
- **Request Body**:
  ```json
  {
    "query": "2024年度の予算編成方針は？",
    "conversation_id": "conv-12345"
  }
  ```
- **Response Body**:
  ```json
  {
    "answer": "2024年度の予算編成方針は、デジタル化の推進と...",
    "citations": [
      {
        "title": "2024_Budget_Guideline.pdf",
        "uri": "gs://bucket-name/docs/2024_Budget_Guideline.pdf",
        "snippets": ["デジタル化の推進を最優先課題とし..."]
      }
    ]
  }
  ```

### 4.2 POST /v1/documents/upload
- **Request Body (Multipart)**:
  - `file`: バイナリデータ
  - `metadata`: `{ "department_id": "sales", "category": "guideline" }`
- **Response Body**:
  ```json
  {
    "document_id": "doc-789",
    "status": "indexing"
  }
  ```

### 4.3 POST /v1/integration/transform
- **Request Body**:
  ```json
  {
    "source_system": "legacy-erp",
    "raw_data": { "emp_id": "E001", "name": "Tanaka" }
  }
  ```
- **Response Body**:
  ```json
  {
    "transformed_data": { "employee_id": "E001", "full_name": "Tanaka", "processed_at": "2024-05-20T10:00:00Z" }
  }
  ```

## 5. 監査ログ
- **記録項目**: タイムスタンプ, ユーザーID, `department_id`, メソッド, パス, ステータスコード, 検索キーワード（匿名化検討）, 実行時間。
- **保存先**: Cloud Logging
