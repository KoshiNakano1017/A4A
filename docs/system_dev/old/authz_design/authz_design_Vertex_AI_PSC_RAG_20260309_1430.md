# 認証・認可設計：Vertex AI PSC RAG

## 1. 方針
- **クライアントから `department_id` を受け取っても信頼しない**（改ざん前提）
- **サーバ側で `department_id` を確定**し、検索/生成/ログに必ず適用する

## 2. IdP（採用）
- **候補**: Cloud Identity / Google Workspace / Firebase Auth
- **採用（暫定）**: Google Identity（OIDC）を前提（実装時に確定）

## 3. トークンと検証
- **入力**: `Authorization: Bearer <ID_TOKEN>`
- **検証**:
  - 署名検証（JWK）
  - `iss`/`aud`/`exp`/`iat`
  - 必要な claim の存在

## 4. `department_id` の確定点（改ざん防止）
- **確定点**: バックエンドAPI（Cloud Run/GKE）
- **取得元（優先順）**:
  1. トークン claim（例: `dept_id` / `department_id`）
  2. `sub`（user_id）をキーにDBから参照（ユーザー管理テーブル）
- **禁止**: リクエストボディ/クエリパラメータの `department_id` を認可に利用すること

## 5. 認可モデル
- **一般ユーザー**:
  - `/api/search`, `/api/ask` のみ利用
  - 検索は必ず `department_id` フィルタを付与
- **管理者**:
  - `/api/documents` 登録/削除を許可
  - 管理者判定はトークン claim（例: `roles: ["admin"]`）またはDBの `user.role`

## 6. 監査ログ（認可観点）
- `request_id`, `user_id`, `department_id`（確定値）, `endpoint`, `decision`（allow/deny）, `reason`

## 7. テスト観点
- `department_id` をリクエストで偽装しても、結果が変わらない（サーバ確定が優先）
- トークン無効/期限切れで `401`
- 他部署データへのアクセスが `403` または空結果（仕様で統一）
