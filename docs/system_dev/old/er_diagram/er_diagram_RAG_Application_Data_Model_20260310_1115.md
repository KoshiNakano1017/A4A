# ER図：RAG アプリケーション データモデル

## 用語定義
- **PSC**: Private Service Connect

```mermaid
er_diagram
    DEPARTMENT ||--o{ USER : "has members"
    DEPARTMENT ||--o{ DOCUMENT : "owns"
    USER ||--o{ SEARCH_LOG : "performs"
    DOCUMENT ||--o{ SEARCH_LOG : "retrieved in"

    USER {
        string user_id PK "User unique ID"
        string name "User full name"
        string email "User email address"
        string department_id FK "Foreign key to Department"
        string role "User role (admin|user)"
        datetime created_at
    }

    DEPARTMENT {
        string department_id PK "Department code (DEPT-XXX)"
        string name "Department name"
        string parent_id FK
        datetime created_at
    }

    DOCUMENT {
        string document_id PK "Unique document ID"
        string gcs_uri "gs://..."
        string title "Original filename"
        string category "Standard|Technical|Legal"
        string department_id FK "Owner department code"
        string search_index_id "Vertex AI Search doc ID"
        datetime uploaded_at
    }

    SEARCH_LOG {
        string log_id PK
        string user_id FK
        string query "Masked query text"
        string department_id
        integer result_count
        datetime search_at
    }
```

## 実装遵守規則
1.  **認可の強制**: API層で `user.department_id` を取得し、全ての検索クエリに `filter="department_id: ANY(\"<dept_id>\")"` を強制すること。
2.  **不整合防止**: `DOCUMENT` 削除時は、Firestore, Vertex AI Search, GCS の3箇所を整合的に削除すること。
