# 永続化設計：Vertex AI PSC RAG

## 用語定義
- **PSC**: Private Service Connect

## 1. データベース選定
- **採用**: Firestore (Native Mode)
- **評価**: 100同時接続および90日のログ保持要件に対して、オートスケーリングと TTL (Time To Live) 機能により十分に対応可能。

## 2. スキーマ修正
- `documents` コレクション:
    - `category` (string): Standard|Technical|Legal を追加。
- **インデックス**:
    - `department_id` (ASC) + `category` (ASC) + `uploaded_at` (DESC) の複合インデックスを作成。

## 3. PII保護
- `search_logs` の `query` フィールドには、Cloud DLP API でマスキング済みのテキストを保存する。
