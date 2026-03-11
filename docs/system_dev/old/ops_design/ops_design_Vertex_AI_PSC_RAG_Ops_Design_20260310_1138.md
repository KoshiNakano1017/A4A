# 運用設計：Vertex AI PSC RAG & API連携基盤

## 1. SLO 定義 (Performance SLO)
| 指標 | 目標値 | 測定区間 | 備考 |
| :--- | :--- | :--- | :--- |
| 検索・生成レイテンシ | 5.0s 以内 (p95) | API 受信 〜 レスポンス送信 | RAG 全体の体験 |
| API 稼働率 | 99.9% | 月間合計時間 | |
| データ整形成功率 | 99.5% | Application Integration 実行数 | |

## 2. 監視指標 (Monitoring)
- **Cloud Monitoring**:
    - `run.googleapis.com/request_count`: 5xx エラー率が 1% を超えたらアラート。
    - `discoveryengine.googleapis.com/request_count`: Vertex AI Search のクォータ超過を監視。
- **アラート条件**:
    - Critical: API サーバーの死活監視失敗 (5分継続)。
    - Warning: レイテンシ p95 が 10s を超過。

## 3. ログ項目 (Logging)
Cloud Logging に以下の構造化ログを出力する。
- `request_id`: トレース用 ID
- `user_id`: UID
- `department_id`: ユーザーの所属部署
- `action`: `ASK_QUERY`, `UPLOAD_DOC`, `TRANSFORM_DATA`
- `latency_ms`: 処理時間
- `result_count`: 検索ヒット数

## 4. セキュリティ・CMEK 運用
- **CMEK (Cloud KMS)**:
    - キーのローテーション: 90日ごとに自動ローテーション。
    - 権限: `service-project-id@gcp-sa-discoveryengine.iam.gserviceaccount.com` に `roles/cloudkms.cryptoKeyEncrypterDecrypter` を付与。
- **PII マスク**: Cloud DLP を通し、ログ保存前に機密情報を自動的に匿名化（DLP 検査失敗時はログ出力を停止しエラー通知）。

## 5. インシデント対応
- **切り分けフロー**:
    1. PSC 接続エラー確認 (Network Intelligence Center)
    2. Vertex AI Search サービス稼働状況確認 (Google Cloud Status Dashboard)
    3. Application Integration フローの実行ログ確認 (Visualizer)
