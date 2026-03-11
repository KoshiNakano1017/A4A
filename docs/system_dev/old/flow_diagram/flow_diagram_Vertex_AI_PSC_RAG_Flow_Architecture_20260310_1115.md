# システム構成図: Vertex AI PSC RAG

## 用語定義
- **PSC**: Private Service Connect

## 構成図（Mermaid）

```mermaid
flowchart LR
    subgraph クライアント
        User[ユーザ]
        App[アプリケーション]
    end

    subgraph GCP
        subgraph Vertex AI
            Search[Vertex AI Search]
            Embed[Embedding API]
        end
        DataPipeline["Pipeline / Store / Connector"]
        GCS[Cloud Storage]
    end

    User --> App
    App -->|検索クエリ + dept_id フィルタ| Search
    App -->|認可チェック| DataPipeline
    DataPipeline --> GCS
    Search -->|メタデータ・チャンク参照| DataPipeline
```

## フロー概要
- 全ての通信は PSC エンドポイントを経由し、VPC Service Controls によって境界外へのデータ流出を防御する。
- 認可（部署境界）はアプリケーション側のバックエンドで強制され、ユーザーが指定した `department_id` をそのまま信用しない。
