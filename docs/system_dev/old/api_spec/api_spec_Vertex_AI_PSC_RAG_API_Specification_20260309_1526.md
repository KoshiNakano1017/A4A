# API仕様書：Vertex AI PSC RAG

## 用語定義
- **PSC**: Private Service Connect

## 1. 認証・認可
- **認証**: `Authorization: Bearer <ID_TOKEN>` (Google Identity OIDC)
- **認可**: 
    - `department_id`: トークンの `dept_id` claim からサーバー側で確定。
    - 管理者権限: トークンの `roles` claim に `admin` を含むこと。

## 2. エンドポイント

### 2.1 質問（検索＋生成）
- **POST** `/api/ask`
- **Request**: `{"query": "string", "category": "string"}`
- **認可**: `dept_id` による自動フィルタリング。

### 2.2 ドキュメント削除
- **DELETE** `/api/documents/{document_id}`
- **認可条件**: 
    1.  リクエスト者が `admin` ロールを保持していること。
    2.  対象ドキュメントの `department_id` がリクエスト者の `dept_id` と一致すること（またはシステム管理者権限）。
- **Response**: `200 OK` { "status": "deleted" } / `403 Forbidden` (権限不足)
