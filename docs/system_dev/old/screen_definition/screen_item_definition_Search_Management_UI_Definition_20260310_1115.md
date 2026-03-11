# 画面項目定義書：検索・ドキュメント管理 UI

## 用語定義
- **PSC**: Private Service Connect

## 1. ドキュメント検索画面
| 項目名 | 物理名 | 型 | 必須 | バリデーション / 制約 |
| :--- | :--- | :--- | :--- | :--- |
| 検索キーワード | query | String | Yes | 2-512文字 |
| 検索フィルター | category | Enum | No | `["Standard", "Technical", "Legal"]` |

## 2. ドキュメント登録画面
| 項目名 | 物理名 | 型 | 必須 | バリデーション / 制約 |
| :--- | :--- | :--- | :--- | :--- |
| データストアID | data_store_id | String | Yes | `^[a-z0-9]([a-z0-9-_]{0,61}[a-z0-9])?$` |
| ドキュメント部署 | target_dept_id | String | Yes | `^[A-Z0-9-]{1,20}$` |
| カテゴリ | category | Enum | Yes | `["Standard", "Technical", "Legal"]` |
| ファイル添付 | upload_file | File | Yes | Max 100MB / .pdf, .docx, .html |

## 3. 遵守規則
- クライアントサイドでの正規表現チェックを必須とし、不正な ID 形式による API エラーを未然に防ぐ。
