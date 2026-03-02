# 下流チーム成果物の配置ルール（downstream/）

このディレクトリには、**上流チーム（architect_agent + review_agent）が確定させた設計資料（`docs/system_dev`）を入力として、下流チーム（`agent_4_agent` 配下のエージェント群）が作成する成果物**を格納します。

## ルート

- 物理パス: `C:\Users\nakano-koshi\project\A4A\downstream`
- Git リポジトリ上のパス: `downstream/`

## 構成ポリシー

- 機能（feature）ごとに 1 フォルダを作成します。
- 各機能フォルダの中に、**ソースコード** と **下流ドキュメント**（詳細設計・API設計・単体テスト仕様・テスト結果）を格納します。
- **ファイル名にバージョンは付けない**（v1/v2/Final 等は禁止）。最新版は常に同じファイル名で管理し、バージョンは Git の履歴で追跡します。

## ディレクトリ構成（例）

```text
downstream/
  feature_x/
    src/                      # この機能で追加・変更したソースコード
    docs/
      detail_design.md        # 詳細設計書（正本）
      api_design.md           # API設計書（正本）
      unit_test_spec.md       # 単体テスト仕様書（正本）
      unit_test_report.md     # 単体テスト結果報告書（正本）
    old/                      # （必要になったら）過去版退避用
      docs/...
      src/...
```

## 運用ルール

- **入力**: 上流チームが `docs/system_dev/` に保存した最新の設計資料（ER図・構成図・画面定義など）を唯一の正本として参照します。
- **出力**: 下流チーム（`agent_4_agent` 配下のエージェント群）は、上記構成に従って `downstream/{feature_name}/` 配下に成果物を出力します。
- ドキュメントは上流と同様、**「ファイル名は固定・バージョンは Git で管理」** を原則とします。将来的に必要であれば、`old/` 以下にタイムスタンプ付きで退避するツールを追加します。

