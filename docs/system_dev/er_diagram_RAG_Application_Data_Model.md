# ER図：RAG Application Data Model

## 用語定義
- **PSC**: Private Service Connect。

## ER図 (Mermaid)
```mermaid
erDiagram
    DEPARTMENT ||--o{ USER : "belongs_to"
    DEPARTMENT ||--o{ DOCUMENT : "owns"
    USER ||--o{ SEARCH_HISTORY : "performs"
    DOCUMENT ||--o{ CITATION : "referenced_in"
    SEARCH_HISTORY ||--o{ CITATION : "includes"

    USER {
        string uid PK "Firebase UID"
        string email
        string department_id FK
        string role "USER, DEPT_ADMIN, SYS_ADMIN"
        timestamp created_at
    }

    DEPARTMENT {
        string department_id PK "Unique Dept ID"
        string department_name
        string data_store_id "Vertex AI Search Data Store ID (Mapping to GCP Infra)"
    }

    DOCUMENT {
        string document_id PK "Unique Doc ID"
        string title
        string gcs_uri
        string department_id FK
        string category "guideline, manual, etc."
        string status "INDEXING, ACTIVE, ERROR"
        timestamp uploaded_at
    }

    SEARCH_HISTORY {
        string search_id PK
        string uid FK
        string query
        string answer
        timestamp timestamp
    }

    CITATION {
        string citation_id PK
        string search_id FK
        string document_id FK
        string snippet
    }
```

## 補足事項
- **`data_store_id` について**: `DEPARTMENT` テーブルに保持している `data_store_id` は、部署ごとの Vertex AI Search リソース（データストア）を特定するためのインフラ連携用 ID です。
- **インフラ分離**: 物理的なリソース配置（VPC SC / PSC）と、論理的なデータ分離（Firestore / Vertex AI Search Data Store）の紐付けに利用されます。詳細なマッピング方針はフロー図を参照してください。
