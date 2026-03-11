# API仕様書：Vertex AI PSC RAG

## 1. 概要
- **目的**: 社内ドキュメント検索（Vertex AI Search）と回答生成（Gemini）を閉域（PSC）で提供する。
- **認可**: `department_id` による部署単位のアクセス制御を必須とする。

## 2. 認証・認可（API観点）
- **認証**: `Authorization: Bearer <ID_TOKEN>`（検証はバックエンドで実施）
- **認可**: `department_id` はクライアント入力を信頼せず、トークン/IDP情報からサーバで確定する。

## 3. 共通仕様
- **Content-Type**: `application/json`
- **リクエストID**: `X-Request-Id`（任意）。未指定時はサーバが採番。
- **エラー形式**:

```json
{
  "error": {
    "code": "string",
    "message": "string",
    "details": {}
  }
}
```

## 4. エンドポイント

### 4.1 検索（検索のみ）
- **POST** `/api/search`
- **認可**: department境界を必須
- **Request**

```json
{
  "query": "string",
  "category": "Standard|Technical|Legal",
  "page_size": 10,
  "page_token": "string"
}
```

- **Response**

```json
{
  "results": [
    {
      "document_id": "string",
      "title": "string",
      "snippet": "string",
      "score": 0.0
    }
  ],
  "next_page_token": "string"
}
```

### 4.2 質問（検索＋生成）
- **POST** `/api/ask`
- **Request**

```json
{
  "query": "string",
  "category": "Standard|Technical|Legal",
  "stream": false
}
```

- **Response（非ストリーミング）**

```json
{
  "answer": "string",
  "citations": [
    {
      "document_id": "string",
      "title": "string",
      "gcs_uri": "string",
      "excerpt": "string"
    }
  ]
}
```

### 4.3 ドキュメント登録
- **POST** `/api/documents`
- **Content-Type**: `multipart/form-data`
- **Form fields**
  - `data_store_id`（string, required）
  - `target_dept_id`（string, required）
  - `kms_key_path`（string, required）
  - `upload_file`（file, required）
- **Response**

```json
{
  "document_id": "string",
  "status": "accepted|indexed|failed"
}
```

### 4.4 ドキュメント削除
- **DELETE** `/api/documents/{document_id}`
- **認可**: 管理者権限（要定義）
- **Response**

```json
{ "status": "deleted" }
```

## 5. ステータスコード（最低限）
- `200`: 成功
- `202`: 受領（非同期処理）
- `400`: バリデーションエラー
- `401`: 未認証
- `403`: 認可失敗（部署境界/権限）
- `404`: 対象なし
- `409`: 競合（重複登録等）
- `429`: レート制限
- `500`: サーバ内部エラー
- `503`: 依存サービス障害（Vertex AI Search/Gemini等）
