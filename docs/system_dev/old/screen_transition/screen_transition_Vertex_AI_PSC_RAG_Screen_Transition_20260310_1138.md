# 画面遷移図：Vertex AI PSC RAG

```mermaid
graph TD
    Login[ログイン画面] --> Auth{認証成否}
    Auth -- 成功 (一般ユーザー) --> Search[検索メイン画面]
    Auth -- 成功 (管理者) --> AdminDash[管理ダッシュボード]
    
    Search -->|検索実行| SearchRes[検索結果表示]
    SearchRes -->|引用詳細| DocDetail[ドキュメントプレビュー]
    
    AdminDash -->|メニュー選択| Upload[ドキュメント登録画面]
    AdminDash -->|メニュー選択| IntegMon[連携基盤モニタ画面]
    
    Upload -->|登録完了| AdminDash
    IntegMon -->|詳細確認| IntFlow[Application Integration デザイナー]
    
    Auth -- 失敗 --> Login
```

## 画面一覧
1. **ログイン画面**: Google Identity Platform を利用。
2. **検索メイン画面**: チャット形式の RAG インターフェース。
3. **管理ダッシュボード**: 統計情報と各機能へのリンク。
4. **ドキュメント登録画面**: ファイルアップロードとメタデータ設定。
5. **連携基盤モニタ画面**: Application Integration の実行履歴。
