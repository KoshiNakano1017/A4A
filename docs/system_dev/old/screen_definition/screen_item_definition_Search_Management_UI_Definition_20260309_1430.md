# 画面項目定義書：検索・ドキュメント管理 UI

## 1. ドキュメント検索画面 (Search Page)
| 項目名 | 物理名 | 型 | 必須 | バリデーション / 制約 | 説明 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 検索キーワード | query | String | Yes | 2-512文字 | 検索クエリ本体 |
| 所属部署ID | user_dept_id | String | (Auto) | `^[A-Z0-9-]{1,20}$` | ユーザーセッションから自動取得・不変 |
| 検索フィルター | category | Enum | No | `["Standard", "Technical", "Legal"]` | 検索対象ドキュメントの種別 |

## 2. ドキュメント登録画面 (Upload Page)
| 項目名 | 物理名 | 型 | 必須 | バリデーション / 制約 | 説明 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| データストアID | data_store_id | String | Yes | `^[a-z0-9-_]{1,63}$` | Vertex AI Search の Data Store ID |
| ドキュメント部署 | target_dept_id | String | Yes | `^[A-Z0-9-]{1,20}$` | 閲覧可能にする部署を指定 |
| CMEK鍵パス | kms_key_path | String | (Set) | `projects/.*/locations/.*/keyRings/.*/cryptoKeys/.*` | 暗号化に使用する KMS キーのフルパス |
| ファイル添付 | upload_file | File | Yes | Max 100MB / .pdf, .docx, .html | Vertex AI Search サポート形式 |

## 3. 実装・テストにおける遵守規則
1.  **クライアントサイド・バリデーション**: `data_store_id` 等の ID 系項目は、必ず上記正規表現に基づき、不正な文字（特に記号や大文字）を入力時に遮断すること。
2.  **API リクエスト制約**: API 側でも同様のバリデーションを行い、違反した場合は `400 Bad Request` とエラーコードを返すこと。
3.  **セキュリティ規則（CMEK）**: KMS 鍵パスが指定されていない場合、または権限がない場合は、ドキュメントのアップロードを拒否するロジックを実装すること。
4.  **認可テスト基準**: 所属部署以外の `department_id` を API リクエストで意図的に送信した場合、`403 Forbidden` または 空の結果が返ることを確認する。
