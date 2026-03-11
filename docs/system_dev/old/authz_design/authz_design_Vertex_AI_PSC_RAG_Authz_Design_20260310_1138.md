# 認証・認可設計：Vertex AI PSC RAG & API連携基盤

## 1. 認証 (Authentication)
- **IdP**: Google Cloud Identity Platform (Firebase Authentication)
- **認証フロー**: OAuth 2.0 / OIDC Authorization Code Flow with PKCE
- **トークン形式**: JSON Web Token (JWT)
- **トークン検証項目**:
    - `iss`: `https://securetoken.google.com/<PROJECT_ID>`
    - `aud`: `<PROJECT_ID>`
    - `exp`: 現在時刻以前であること
    - `sub`: 有効なユーザーID (UID) であること
    - `clock_skew`: 5分以内を許容

## 2. 認可 (Authorization)
- **部署 ID (`department_id`) の決定**:
    - 各ユーザーは Firestore または LDAP/AD 連携により特定の `department_id` に紐づく。
    - API サーバーは、リクエスト受信時に Firestore の `users` コレクションから `department_id` を取得し、コンテキストに保持する。
- **認可の強制点**:
    - **Vertex AI Search 検索時**: 検索 API の `filter` パラメータに `department_id: ANY("current_user_dept_id")` をサーバーサイドで強制付与する。
    - **ドキュメント参照/管理**: Firestore および GCS の IAM 条件 (Attribute-based access control - ABAC) またはアプリケーション層でのチェックにより、他部署のドキュメント ID へのアクセスを拒否する。
- **管理者権限**:
    - `is_admin: true` フラグを持つユーザーのみが、管理用エンドポイント（ドキュメント登録等）を実行可能。

## 3. ロール定義
| ロール名 | 説明 | 権限範囲 |
| :--- | :--- | :--- |
| **一般ユーザー** | 自身の部署のドキュメントを検索・閲覧可能 | `v1/ask`, `v1/documents` (GET) |
| **部署管理者** | 自身の部署のドキュメントを管理可能 | `v1/documents/upload`, `v1/documents` (DELETE) |
| **システム管理者** | 全部署の統計閲覧、システム設定、API連携基盤の管理 | `v1/integration/*`, 全ての管理機能 |

## 4. 想定脅威と対策
- **水平越権 (Horizontal Privilege Escalation)**:
    - 対策: `department_id` をクライアント側から渡さない。サーバーサイドで常にユーザー情報（トークン）から所属部署を確定させ、フィルタに反映する。
- **リプレイ攻撃**:
    - 対策: JWT の `exp` (有効期限) を短く（例: 1時間）設定し、`jti` (JWT ID) による使い回し防止（必要に応じて）を行う。
- **権限昇格**:
    - 対策: IAM による最小権限の徹底。API サーバー実行用のサービスアカウントには、各部署のデータフォルダへのアクセス権限のみを動的に与える（またはアプリケーション側で一元管理）。
