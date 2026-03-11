# 永続化設計：Vertex AI PSC RAG

## 1. 対象データ
- `USER` / `DEPARTMENT` / `DOCUMENT` / `SEARCH_LOG`

## 2. 採用（暫定）
- **DB**: Firestore（サーバレス、スキーマ柔軟、検索ログ蓄積に適合）
- **理由**:
  - 同時100ユーザー規模の要件に十分
  - 低運用負荷
  - `department_id` をキーにアクセス制御・クエリ設計しやすい

## 3. コレクション設計（案）
- `users/{user_id}`
  - `department_id`, `name`, `email`, `role`, `created_at`
- `departments/{department_id}`
  - `name`, `parent_id`, `created_at`
- `documents/{document_id}`
  - `department_id`, `gcs_uri`, `title`, `search_index_id`, `uploaded_at`
- `search_logs/{log_id}`
  - `user_id`, `department_id`, `query`, `result_count`, `search_at`

## 4. インデックス（必須）
- `documents`:
  - `department_id` + `uploaded_at`（一覧/管理）
- `search_logs`:
  - `department_id` + `search_at`
  - `user_id` + `search_at`

## 5. 保持（運用と連動）
- `search_logs`: 90日（要件で変更可）
- `documents`: 削除要求があれば論理削除→物理削除（手順は下記）

## 6. 削除整合（最重要）
- ドキュメント削除時は以下を **トランザクション/補償処理**として実装する：
  1. DBの `documents/{document_id}` を削除（または `deleted=true`）
  2. Vertex AI Search の doc（`search_index_id`）削除
  3. GCSオブジェクト削除
- 途中失敗時は再実行できるように **冪等**にする（deleteは存在しなくても成功扱い等）

## 7. テスト観点
- 部署フィルタなしのDBクエリが無い（コードレビューで禁止）
- 削除が途中失敗しても再実行で整合が取れる
