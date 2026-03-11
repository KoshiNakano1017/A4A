# 認証・認可設計：Vertex AI PSC RAG

## 用語定義
- **PSC**: Private Service Connect

## 1. IdP 構成
- **IdP**: Google Identity (OIDC) に確定。
- **JWT Claims**:
    - `dept_id`: ユーザーの所属部署コード。
    - `roles`: ユーザーの権限リスト（例: `["admin", "user"]`）。

## 2. 認可ロジック
- **部署境界**: 全ての API はトークンの `dept_id` を元に、Firestore および Vertex AI Search の `filter` を強制適用する。
- **管理者判定**: `/api/documents` 系の書込・削除エンドポイントでは、`roles` claim に `admin` が含まれていることを検証する。
- **改ざん防止**: リクエストボディに含まれる `department_id` は無視し、常に JWT から抽出した値を使用する。
