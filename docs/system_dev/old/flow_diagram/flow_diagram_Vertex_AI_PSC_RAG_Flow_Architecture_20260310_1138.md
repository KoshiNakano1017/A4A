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
