# フロー図：Vertex AI PSC RAG システム構成

## 用語定義
- **PSC**: Private Service Connect。Google Cloud のサービスを VPC 内部からプライベートに利用するためのネットワーク技術。

## 構成図 (Mermaid)
```mermaid
graph TB
    subgraph "Consumer VPC (On-Prem / Corporate Network)"
        User((User))
        Admin((Admin))
    end

    subgraph "Google Cloud Project (Producer VPC)"
        subgraph "VPC SC / Service Perimeter"
            API[API Server / GKE / Cloud Run]
            Auth[Identity Platform]
            
            subgraph "Integration Layer"
                AppInt[Application Integration]
                CF[Cloud Functions - Python]
            end

            subgraph "Storage Layer"
                GCS[(Google Cloud Storage)]
                DB[(Firestore)]
            end

            subgraph "Vertex AI Search"
                VAIS[Vertex AI Search Engine]
                PSC_EP[PSC Endpoint]
            end
        end
    end

    %% Communication Flow
    User -->|HTTPS| API
    Admin -->|HTTPS| API
    API -->|Auth Check| Auth
    API -->|Metadata| DB
    API -->|Fetch Docs| GCS
    
    %% RAG Flow via PSC
    API -->|Internal Call| PSC_EP
    PSC_EP -->|Private Connect| VAIS
    
    %% Data Integration Flow
    API -->|Invoke| AppInt
    AppInt -->|Custom Logic| CF
    AppInt -->|Store| DB
    AppInt -->|Sync| VAIS
```

## インフラ・データマッピング方針
1.  **認可の強制点**: API サーバーが、Firestore から取得したユーザーの `department_id` に基づいて、リクエスト先の `data_store_id` を確定します。
2.  **PSC エンドポイント**: 各 Vertex AI Search のデータストア（部署単位、または共通）へのアクセスは、一元化された PSC エンドポイントを介して行われます。
3.  **VPC SC**: 全リソースをサービス境界内に配置し、インターネットへのデータ持ち出しを防止します。
