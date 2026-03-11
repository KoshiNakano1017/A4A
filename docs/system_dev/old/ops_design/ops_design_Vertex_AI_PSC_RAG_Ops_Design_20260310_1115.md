# 運用設計：Vertex AI PSC RAG

## 用語定義
- **PSC**: Private Service Connect

## 1. ログとPII保護
- **方針**: 検索クエリを監査ログとして保存する際、個人情報（PII）の流出を防止する。
- **実装**: Backend API から Cloud Logging/Firestore へ出力する前に、Cloud DLP API を呼び出し、人名・住所・電話番号等の PII 要素を `[PII_REDACTED]` に置換する。

## 2. セキュリティ運用
- **CMEK**: サービスエージェントに対して、KMS キーの `roles/cloudkms.cryptoKeyEncrypterDecrypter` を付与し、定期的なキーローテーションを構成する。
