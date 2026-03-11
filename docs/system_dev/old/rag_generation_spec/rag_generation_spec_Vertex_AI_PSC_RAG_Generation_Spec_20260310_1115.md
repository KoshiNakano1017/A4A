# RAG生成仕様：Vertex AI PSC RAG

## 用語定義
- **PSC**: Private Service Connect

## 1. プロンプト構成
- **Grounding**: 検索結果から得られた `department_id` 一致ドキュメントのみをコンテキストとして利用。
- **Citation**: 回答には必ず引用元ドキュメントの `document_id` を含める。
