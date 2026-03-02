# 設計・レビューサイクルの想定ふるまい検証

アーキテクトが「6つの設計資料を正本として再格納した」と報告した場合、**想定どおりのふるまいになっているか**を仕様と実装で検証するためのメモ。

---

## 1. 想定どおりになっている点（仕様との一致）

| 項目 | 想定 | 実装・指示 |
|------|------|------------|
| 旧版の自動削除が不可 | アーキテクトはファイルの削除・一括移動ができない | ✅ ツールは「上書き時に同名ファイルを archive に退避」のみ。Instruction にも「old_versions の作成・他ファイルの移動・削除はできない」と明記。 |
| 正本はバージョン表記なし | v2, v3, Final をファイル名に付けない | ✅ `_canonical_title` で v1/v2/v3/Final を除去し、`suffix` は使わない。常に「プレフィックス_タイトル.md」で保存。 |
| 上書き時に1世代バックアップ | 同名ファイルがあれば archive に日時付きで退避 | ✅ `path.exists()` のとき `archive/{stem}_{YYYYMMDD_HHMM}.{ext}` に `rename` してから上書き。 |
| 設計要約とPMへのレビュー依頼 | 保存後に約13行の要約を出し、PMにレビュー依頼を促す | ✅ Instruction に明記。アーキテクトが実際に要約を出し「レビューを依頼してください」と書くかは応答次第。 |
| レビューは read_design_doc で検証 | ER図とインフラの分離・API制約を自動検証し Go/要修正 | ✅ Review Agent に read_design_doc_tool を追加し、Instruction に検証項目と判定（Go/要修正）を明記。 |
| PMはGoだけユーザーに報告 | 要約とレビュー結果を統合し、通過したものだけ報告 | ✅ Coordinator Instruction に「レビューが Go になった成果物だけを完了・採用可として報告」と明記。 |

---

## 2. ずれが起きうる点（要確認）

### 2.1 実際のファイル名は「種別プレフィックス付き」になる

- **アーキテクトが言いがちな名前**: `Data_Entity_Definition.md`, `System_Requirement_Specification.md`, `Screen_Item_Definition.md` など。
- **ツールが実際に作る名前**: 常に **`{doc_type のプレフィックス}_{title}.md`**。
  - 例: `er_diagram_Data_Entity_Definition.md`, `flow_diagram_System_Requirement_Specification.md`, `screen_item_definition_Screen_Item_Definition.md`
- **結論**: 「正本のファイル名」は、**docs/system_dev 直下の「種別_名前.md」** が正本。アーキテクトが「Data_Entity_Definition.md を正本にした」と書いていても、実ファイルは `er_diagram_Data_Entity_Definition.md`。レビュー依頼や read_design_doc に渡すパスはこの実名にする必要がある。

### 2.2 「6つの設計資料」と doc_type の対応

- 利用できる doc_type は 5 種類: `flow_diagram`, `er_diagram`, `user_manual`, `screen_definition`, `screen_transition`。
- 6 ファイルにするには、いずれかを 2 回使う必要がある（例: 要件仕様書とシステム構成図の両方に `flow_diagram` を使い、タイトルで区別）。
- 想定どおりのふるまいとしては、6 回 `write_design_doc` が呼ばれれば 6 ファイルが保存される。

### 2.3 アーキテクトがツールを呼ばずに「保存した」とだけ言う場合

- Instruction では「保存したと報告する場合は必ず write_design_doc を呼ぶ」と書いてあるが、守られないと**実際にはファイルが増えない**。
- 想定どおりにするには: アーキテクトの応答で **write_design_doc の呼び出し（またはツール結果の path/message）がログに出ているか** を確認する必要がある。

---

## 3. 現在の docs/system_dev の状態（このリポジトリ）

- 直下にあるのは次のみ（archive 除く）:
  - `flow_diagram_Vertex_AI_PSC_RAG.md`
  - `er_diagram_RAG_Application_Data_Model.md`
- そのため、「6つの設計資料を再格納した」というアーキテクトの報告が**このワークスペースの実ファイルと一致しているか**は、その会話がこの環境でツールを実際に 6 回呼んだ結果かどうかで変わる。別環境・別セッションや、ツール未使用の応答の場合は、ディスク上に 6 ファイルは存在しない。

---

## 4. 想定どおりかどうかを確認する手順

1. **アーキテクト実行後**
   - アーキテントのログで `write_design_doc` が、想定する設計書の数だけ呼ばれているか確認する。
   - `docs/system_dev/` 直下に、想定どおりの「種別_タイトル.md」が並んでいるか確認する。
   - 必要なら `docs/system_dev/archive/` に、上書き前の日時付きファイルが退避されているか確認する。

2. **レビュー依頼時**
   - PM が review_agent に渡しているパスが、実在するファイル名（例: `er_diagram_Data_Entity_Definition.md`）になっているか確認する。
   - review_agent が `read_design_doc(ファイル名またはパス)` を呼び、戻り値の content でレビューしているか確認する。
   - レビュー結果に **「判定: Go」または「判定: 要修正」** が含まれているか確認する。

3. **PM の報告**
   - ユーザーに「完了・採用可」として出しているのが、**レビューで Go になった成果物だけ**か確認する。要修正のものは修正・再レビュー後に報告される想定。

---

## 5. 結論

- **仕様・Instruction・ツールの動きは、設計・レビューサイクルの「想定」と一致している。**
- **想定どおりのふるまいにするには次が重要:**
  - アーキテクトが**必ず write_design_doc を呼んで**保存していること。
  - 正本のファイル名は **`種別_タイトル.md`** であることをPM・レビュー側が前提にしていること。
  - PM がレビュー結果の **Go/要修正** を見て、Go のものだけをユーザーに報告していること。
- アーキテクトの「6つ再格納した」という文言だけでは、実際に 6 ファイルがこの環境に保存されたかは分からない。上記の手順でログと `docs/system_dev/` の中身を確認すると、「できてる？」に答えられる。
