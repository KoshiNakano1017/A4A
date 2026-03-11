# 永続化設計：Vertex AI PSC RAG & API連携基盤

## 1. 採用技術と理由
- **Google Cloud Storage (GCS)**: 非構造化データ（ドキュメント、画像等）の保存用。
- **Firestore (Native Mode)**: 構造化メタデータ（ユーザー情報、部署、ドキュメント属性）の保存用。NoSQL であるため、メタデータのスキーマ変更に柔軟に対応可能。
- **Vertex AI Search**: ドキュメントの検索および回答生成用。ベクトルデータベースとしての役割を担う。

## 2. コレクション (テーブル) 設計

### 2.1 Firestore: `users`
| フィールド名 | 型 | 必須/任意 | 説明 |
| :--- | :--- | :--- | :--- |
| `uid` | String | 必須 (Key) | Firebase Auth UID |
| `email` | String | 必須 | ユーザーのメールアドレス |
| `department_id` | String | 必須 | 所属部署 ID |
| `role` | String | 必須 | `USER`, `DEPT_ADMIN`, `SYS_ADMIN` |
| `created_at` | Timestamp | 必須 | 登録日時 |

### 2.2 Firestore: `documents`
| フィールド名 | 型 | 必須/任意 | 説明 |
| :--- | :--- | :--- | :--- |
| `document_id` | String | 必須 (Key) | ドキュメントのユニーク ID |
| `title` | String | 必須 | ファイル名 / タイトル |
| `gcs_uri` | String | 必須 | `gs://bucket-name/path/to/file` |
| `department_id` | String | 必須 | 所属部署 ID (認可用) |
| `category` | String | 任意 | 分類 (規程、マニュアル等) |
| `status` | String | 必須 | `INDEXING`, `ACTIVE`, `ERROR` |

## 3. インデックス設計
- **Firestore**:
    - `users`: `email` (Unique Index)
    - `documents`: `department_id` (ASC) + `created_at` (DESC) (複合インデックス)
- **Vertex AI Search**:
    - メタデータフィールド `department_id`, `category` に対してフィルタを有効化。

## 4. 保持・削除整合
- **削除フロー**:
    1. ユーザーがドキュメント削除をリクエスト。
    2. API が Vertex AI Search からドキュメントを削除。
    3. GCS から実ファイルを削除。
    4. Firestore のレコードを削除（または論理削除）。
- **不整合対策**: 定期的なバックグラウンドジョブ (Cloud Functions) により、Firestore に存在し GCS に存在しないデータのクリーンアップを実施。

## 5. 監査ログ項目
- `persistence_event`: `INSERT`, `UPDATE`, `DELETE`
- `target_resource`: `Firestore:users`, `GCS:bucket-name/file`
- `actor_uid`: 操作ユーザーの UID
- `result`: `SUCCESS`, `FAILURE` (エラー詳細を含む)
