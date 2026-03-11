# システム構成・フロー図：Vertex AI Search (PSC Edition) RAG

```mermaid
graph TD
    subgraph "Corporate Network (On-Premise / Client)"
        User[End User]
    end

    subgraph "Google Cloud Project (Producer)"
        subgraph "Consumer VPC (User Side)"
            LB[Internal Load Balancer]
            BE["Backend Application (Cloud Run/GKE)"]
            PSC_ENDPOINT["PSC Endpoint (Vertex AI Search)"]
            PSC_KMS["PSC Endpoint (Cloud KMS)"]
        end

        subgraph "Google Managed Services (Producer Side)"
            VAIS[Vertex AI Search]
            LLM["Gemini 1.5 Pro/Flash"]
            GCS["Cloud Storage (CMEK-protected)"]
            KMS[Cloud Key Management Service]
        end

        %% Connections
        User -- "HTTPS (VPN/Interconnect)" --> LB
        LB -- "Request (Closed)" --> BE
        BE -- "Internal Lookup (department_id filter)" --> PSC_ENDPOINT
        PSC_ENDPOINT -- "Private Link (PSC)" --> VAIS
        BE -- "CMEK Operation" --> PSC_KMS
        PSC_KMS -- "Private Link (PSC)" --> KMS
        VAIS -- "Data Fetch" --> GCS
        GCS -- "Decrypt with CMEK" --> KMS
    end

    %% Network Security Rules
    style User fill:#f9f,stroke:#333,stroke-width:2px
    style VAIS fill:#4285F4,stroke:#333,color:#fff
    style PSC_ENDPOINT fill:#FBBC05,stroke:#333
    style GCS fill:#34A853,stroke:#333,color:#fff
```

## アーキテクチャ遵守規則
1.  **PSC 構成の強制**: バックエンドサービス（Cloud Run 等）は、直接インターネットへ抜けず、必ず `Service Directory` に登録された PSC エンドポイントを通じて Vertex AI API を叩くこと。
2.  **VPC Service Controls (VPC SC)**: 境界防御を有効にし、指定した PSC エンドポイント以外からの API アクセスを拒絶する。
3.  **CMEK 権限の分離**: サービスエージェント（Vertex AI / GCS / BigQuery 等）に対し、KMS の `roles/cloudkms.cryptoKeyEncrypterDecrypter` を付与し、かつ他のリソースへのアクセスを禁止する。

## 用語
- **PSC**: Private Service Connect（Google Cloud の閉域接続機構）

## テスト項目（QA合格基準）
- **通信遮断テスト**: インターネットゲートウェイおよび外部 IP を持たない環境で、正常に Vertex AI Search からの回答が得られること。
- **認可境界テスト**: `department_id: A` のユーザーが、`department_id: B` のドキュメントを取得できないことが、ログおよびレスポンスで証明されること。
- **CMEK 暗号化確認**: キーを無効化した際、即座に検索および GCS へのアクセスが失敗すること。
