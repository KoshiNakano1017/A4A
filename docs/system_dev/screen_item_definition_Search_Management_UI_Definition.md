# 画面項目定義書：Vertex AI PSC RAG

## 用語定義
- **PSC**: Private Service Connect。

## 1. 検索画面 (User Search Screen)
| 項目名 | ID | 型 | 必須 | バリデーション / 備考 |
| :--- | :--- | :--- | :--- | :--- |
| 質問入力 | `query_input` | String | ◯ | 最大 500文字 |
| 回答表示 | `answer_display` | Markdown | - | RAG 生成回答を表示 |
| 引用リスト | `citation_list` | List | - | ドキュメント名とスニペットを表示 |
| カテゴリフィルタ | `category_filter` | Dropdown | - | `requirements_definition` 記載のカテゴリ |

## 2. 管理画面：ドキュメントアップロード (Admin Upload Screen)
| 項目名 | ID | 型 | 必須 | バリデーション / 備考 |
| :--- | :--- | :--- | :--- | :--- |
| ファイル選択 | `file_picker` | File | ◯ | PDF, DOCX, TXT / 最大 10MB |
| 部署 ID | `dept_id_input` | String | ◯ | `^[a-zA-Z0-9_]{1,64}$` / 管理者のみ変更可 |
| カテゴリ | `category_input` | String | ◯ | `^[a-zA-Z0-9_]{1,64}$` |
| データストア ID | `data_store_input` | String | ◯ | `^[a-z0-9]([a-z0-9-_]{0,61}[a-z0-9])?$` |
| タイトル | `doc_title` | String | ◯ | ファイル名を初期値とする |

## 3. 管理画面：連携基盤モニタ (Integration Monitor)
| 項目名 | ID | 型 | 備考 |
| :--- | :--- | :--- | :--- |
| 実行ステータス | `flow_status` | Status | SUCCESS / FAILED / RUNNING |
| 連携ログ | `integration_logs` | List | Application Integration の Execution ID と紐付け |
