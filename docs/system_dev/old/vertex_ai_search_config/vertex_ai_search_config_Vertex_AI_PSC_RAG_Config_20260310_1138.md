# Vertex AI Search 設定：Vertex AI PSC RAG & API連携基盤

## 1. 対象リソース
- **Project**: `<PROJECT_ID>`
- **Location**: `global` (または `us-central1`, `asia-northeast1`)
- **Engine**: `Search Engine (RAG)`
- **Data Store**: `Document Data Store`

## 2. メタデータスキーマ定義
Vertex AI Search の各ドキュメントに付与するメタデータの定義。

| フィールド名 | 型 | フィルタ | 表示 | 説明 |
| :--- | :--- | :--- | :--- | :--- |
| `department_id` | String | 有効 | 無効 | 部署 ID (アクセス制御の主軸) |
| `category` | String | 有効 | 有効 | ドキュメントの種類 (規程, マニュアル等) |
| `upload_date` | String (ISO8601) | 有効 | 有効 | アップロード日時 |
| `visibility` | String | 有効 | 無効 | `INTERNAL`, `PUBLIC` |

## 3. Filter 式の厳密な例
検索リクエスト時に `department_id` を強制フィルタリングするための `filter` パラメータ。

- **例1: ユーザー所属部署が `sales` の場合**
  ```bash
  filter: 'department_id: ANY("sales")'
  ```
- **例2: `sales` 部署に所属し、かつ `guideline` カテゴリのドキュメントを検索する場合**
  ```bash
  filter: 'department_id: ANY("sales") AND category: ANY("guideline")'
  ```
- **例3: 特定のドキュメント ID を除外する場合**
  ```bash
  filter: 'department_id: ANY("sales") AND NOT document_id: ANY("doc-123")'
  ```

## 4. 取り込み・削除手順
- **取り込み**:
    1. GCS へのファイルアップロード。
    2. API 経由で `Discovery Engine API` (Inclusion) を呼び出す。
    3. メタデータとして `department_id` 等を JSON 形式で渡す。
- **削除**:
    1. `Discovery Engine API` (Deletion) をドキュメント ID を指定して呼び出す。
    2. 成功後、GCS の実ファイルを削除。
- **再取り込み (更新)**:
    1. 既存ドキュメントを ID 指定で削除後、再度取り込む。

## 5. チャンク方針 (Chunking Policy)
- **分割単位**: `Document-level` または `Page-level` (要件に応じて)
- **最大チャンクサイズ**: 1000 tokens (LLM のコンテキスト制限を考慮)
- **OCR 有無**: PDF/画像形式のドキュメントを扱うため **有効** とする。

## 6. エラー時リトライ方針
- `Discovery Engine API` の呼び出しが失敗した場合、指数バックオフを伴うリトライ (最大3回) を実施。
- 3回失敗時は Firestore のステータスを `ERROR` に変更し、管理画面に通知。
