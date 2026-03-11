# 運用設計：Vertex AI PSC RAG

## 1. ログ設計（Cloud Logging）
- **必須フィールド**
  - `request_id`
  - `user_id`
  - `department_id`（サーバ確定値）
  - `endpoint`
  - `latency_ms`
  - `status_code`
  - `error_code`（ある場合）
- **PII**
  - `query` は個人情報を含みうるため、保存/マスキング方針を定義する（デフォルトは保存しない、必要時のみ部分マスク）

## 2. メトリクス/SLO
- **SLO（要件から転記）**
  - 検索: p95 1.5s以内
  - 生成: p95 5.0s以内（非ストリーミング）
  - 稼働率: 99.9%
- **アラート**
  - 5xx 比率上昇
  - p95 レイテンシ逸脱
  - Vertex AI Search/Gemini の依存エラー増加

## 3. CMEK運用
- KMS key のローテーション手順
- key 無効化時の影響（検索/生成が即失敗する）と復旧手順
- 付与ロールの棚卸し（最小権限）

## 4. 障害対応（最低限）
- 切り分け順序: LB → Backend → PSC → Vertex AI Search/GCS/KMS
- リトライ方針（クライアント/サーバ）とサーキットブレーカー方針（必要なら）

## 5. 監査
- 認可拒否（403）を監査対象として集計（部署境界テストの証跡）
