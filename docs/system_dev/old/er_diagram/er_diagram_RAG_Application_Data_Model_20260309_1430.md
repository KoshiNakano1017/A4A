# ER図：RAG アプリケーション データモデル

```mermaid
erDiagram
    DEPARTMENT ||--o{ USER : "has members"
    DEPARTMENT ||--o{ DOCUMENT : "owns"
    USER ||--o{ SEARCH_LOG : "performs"
    DOCUMENT ||--o{ SEARCH_LOG : "retrieved in"

    USER {
        string user_id PK "User unique ID (Firebase/Cloud Identity)"
        string name "User full name"
        string email "User email address"
        string department_id FK "Foreign key to Department"
        datetime created_at "Record creation timestamp"
    }

    DEPARTMENT {
        string department_id PK "Department code (e.g., DEPT-001)"
        string name "Department name (e.g., Sales)"
        string parent_id FK "Self-referencing for hierarchy"
        datetime created_at "Record creation timestamp"
    }

    DOCUMENT {
        string document_id PK "Unique document ID (UUID/ULID)"
        string gcs_uri "Path to document in GCS (gs://...)"
        string title "Original filename"
        string department_id FK "Owner department code"
        string search_index_id "Vertex AI Search doc ID"
        datetime uploaded_at "Document upload timestamp"
    }

    SEARCH_LOG {
        string log_id PK "Unique log ID"
        string user_id FK "Associated user"
        string query "Search query text"
        string department_id "Department context at search"
        integer result_count "Number of documents retrieved"
        datetime search_at "Timestamp of search"
    }
```

## 実装・QA遵守規則
1.  **認可の強制**: アプリケーション層のAPIエンドポイントは、常にリクエスト者の `user.department_id` を取得し、DBおよびVertex AI Searchのクエリに `filter="department_id: (DEPT-001)"` 等のフィルタを**必ず**含めること。
2.  **IDの正規化**: `department_id` は全て大文字、ハイフン、数字のみを許可し、記号混入によるインジェクションを防止する。
3.  **データ整合性**: `DOCUMENT` の削除時は、Vertex AI Search のインデックスも削除することを保証し、不整合（ゴミデータ）を QA のテスト対象とする。
