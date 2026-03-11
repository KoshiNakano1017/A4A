# 永続化設計：Vertex AI PSC RAG & API連携基盤

## 用語定義
- **PSC**: Private Service Connect。

## 1. 採用技術と理由
- **Google Cloud Storage (GCS)**: 非構造化データ（ドキュメント等）の保存用。
- **Firestore (Native Mode)**: 構造化メタデータ（ユーザー情報、部署、ドキュメント属性）の保存用。
- **Vertex AI Search**: ドキュメントの検索および回答生成用。ベクトルデータベースとしての役割を担う。

## 2. コレクション (テーブル) 設計
### 2.1 Firestore: `users`
- `uid` (Key), `email`, `department_id`, `role`, `created_at`
### 2.2 Firestore: `documents`
- `document_id` (Key), `title`, `gcs_uri`, `department_id`, `category`, `status`, `data_store_id`

## 3. インデックス設計
- **Firestore**: `users`: `email` (Unique Index), `documents`: `department_id` + `created_at` (複合)
- **Vertex AI Search**: `department_id`, `category` に対してフィルタを有効化。

## 4. 保持・削除整合
- 削除フロー: Vertex AI Search -> GCS -> Firestore の順で削除。
- 不整合対策: 定期的なクリーンアップジョブ (Cloud Functions) の実行。
