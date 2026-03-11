# Vertex AI Search 設定：Vertex AI PSC RAG

## 用語定義
- **PSC**: Private Service Connect

## 1. スキーマ定義
- **metadata**:
    - `department_id`: string (Indexing enabled, Filterable)
    - `category`: string (Indexing enabled, Filterable)
- **ID体系**:
    - `data_store_id`: `^[a-z0-9]([a-z0-9-_]{0,61}[a-z0-9])?$`
