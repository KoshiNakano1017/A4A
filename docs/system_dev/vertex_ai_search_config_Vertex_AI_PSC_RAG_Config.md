# Vertex AI Search 設定：Vertex AI PSC RAG & API連携基盤

## 用語定義
- **PSC**: Private Service Connect。

## 1. 対象リソース
- **Project**: `<PROJECT_ID>`
- **Engine**: `Search Engine (RAG)`
- **Data Store**: `Document Data Store`

## 2. メタデータスキーマ定義
| フィールド名 | 型 | フィルタ | 表示 | 説明 |
| :--- | :--- | :--- | :--- | :--- |
| `department_id` | String | 有効 | 無効 | 部署 ID (アクセス制御) |
| `category` | String | 有効 | 有効 | ドキュメントの種類 |
| `data_store_id` | String | 有効 | 有効 | データストア ID |

## 3. Filter 式の厳密な例
- ユーザー所属部署が `sales` の場合: `filter: 'department_id: ANY("sales")'`
- `sales` かつ `guideline` の場合: `filter: 'department_id: ANY("sales") AND category: ANY("guideline")'`

## 4. 取り込み・削除手順
- 取り込み: GCS へのファイルアップロード -> Discovery Engine API 呼び出し。
- 削除: Discovery Engine API (Deletion) -> GCS 削除。

## 5. チャンク方針 (Chunking Policy)
- 分割単位: `Document-level` または `Page-level`
- 最大チャンクサイズ: 1000 tokens (TBD: プロトタイプ後に最適化)
- OCR 有無: **有効** (PDF/画像対応)

## 6. エラー時リトライ方針
- 失敗した場合、指数バックオフを伴うリトライ (最大3回) を実施。
- 3回失敗時は Firestore のステータスを `ERROR` に変更し、管理画面に通知。
