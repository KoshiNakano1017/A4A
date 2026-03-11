# Vertex AI Search 設定：Vertex AI PSC RAG

## 1. 目的
- `department_id` をメタデータとして保持し、検索時にフィルタで部署境界を強制する。

## 2. メタデータスキーマ（案）
- `department_id`: string（必須）
- `category`: string（任意、例: Standard/Technical/Legal）
- `document_id`: string（アプリ側ID）

## 3. フィルタ式（例）
- **部署境界**:
  - `department_id: ("DEPT-001")`
- **部署＋カテゴリ**:
  - `department_id: ("DEPT-001") AND category: ("Legal")`

※ 実装では、Vertex AI Search/Discovery Engine の実フィルタ文法に合わせて最終確定する。

## 4. 取り込み（登録）手順（概要）
1. アップロードされたファイルを GCS に保存（CMEK有効）
2. Vertex AI Search の Data Store にインポート（メタデータ付与）
3. `search_index_id`（検索側のdoc識別子）を `DOCUMENT` に保存

## 5. 削除手順（概要）
1. アプリ側 `DOCUMENT` を削除（または論理削除）
2. Vertex AI Search から `search_index_id` を削除
3. GCS オブジェクトを削除

## 6. PSC/CMEK/権限（最低限）
- PSC 経由で Vertex AI API に到達すること
- CMEK:
  - KMS key を Vertex AI Search/GCS で利用
  - サービスエージェントに暗号/復号ロールを付与（最小権限）
