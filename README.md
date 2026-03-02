# A4A
![A4A Logo](assets/a4a.png)

エージェントを作るためのエージェント(Agent for Agent)です。略してA4Aと呼びます。

<!-- Project Status Badges -->
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![GitHub release](https://img.shields.io/github/v/release/tyukei/A4A)](https://github.com/tyukei/A4A/releases)
[![Last Commit](https://img.shields.io/github/last-commit/tyukei/A4A)](https://github.com/tyukei/A4A/commits/main)

<!-- Community Badges -->
[![Contributing](https://img.shields.io/badge/Contributing-Welcome-green.svg)](CONTRIBUTING.md)
[![Code of Conduct](https://img.shields.io/badge/Code%20of%20Conduct-Contributor%20Covenant-purple.svg)](CODE_OF_CONDUCT.md)
[![Security](https://img.shields.io/badge/Security-Policy-blue.svg)](SECURITY.md)

<!-- GitHub Engagement -->
[![GitHub stars](https://img.shields.io/github/stars/tyukei/A4A.svg?style=social&label=Star)](https://github.com/tyukei/A4A)
---

## クイックスタート

```bash
# リポジトリをクローン
git clone https://github.com/tyukei/A4A.git
cd A4A

# 環境構築
uv sync --frozen
source .venv/bin/activate
cp src/agent_4_agent/.env.example src/agent_4_agent/.env

# .envファイルにGEMINI_API_KEYを設定
# https://aistudio.google.com/api-keys

# Web UI を起動
adk web src/
```

ブラウザで http://127.0.0.1:8000 を開いて、エージェント作成を始めましょう！

```bash
# CLI でエージェントを作成（Web UI 不要）
a4a --idea "作りたいエージェントのキーワード"

# 作成 + GitHub PR 提出
a4a --idea "天気" --pr

# 作成 + PR提出 + レビュー + GitHub issue 起票まで全部
a4a --idea "天気" --pr --issue
```

詳細は [CLI ガイド](docs/usage.md#cli-でエージェントを自動作成するa4a) をご覧ください。

詳細な手順は [セットアップと実行ガイド](docs/setup_and_execution.md) をご覧ください。

---

## ドキュメント

### 基本ガイド

- **[A4Aについて](docs/introduction.md)** - A4Aの概要とできること
- **[セットアップと実行](docs/setup_and_execution.md)** - インストールと基本的な使い方
- **[使い方ガイド](docs/usage.md)** - エージェントの作成から利用まで

### 技術ドキュメント

- **[アーキテクチャ](docs/architecture.md)** - A4Aの全体構成とA2Aの活用方法
- **[A2Aガイド](docs/a2a_guide.md)** - Agent to Agentプロトコルの詳細
- **[ADKチュートリアル](docs/adk_tutorial.md)** - ADKエージェントの作り方

### その他

- **[デプロイメント](docs/deployment.md)** - Agent Engineへのディプロイ方法
- **[CI/CD](docs/cicd.md)** - GitHub Actionsを使った自動化
- **[Why A4A?](docs/why_a4a.md)** - A4Aを作った理由と未来への展望

---

## できること

- **エージェント作成**: ADKでエージェントを対話的に作成
- **PR自動提出**: 作成したエージェントをそのままGitHub PRとして提出
- **品質レビュー**: コード品質・instruction完成度をAIが自動レビューしてissue起票
- **A2A連携**: 作成したエージェントをA2Aでつなげる
- **自動ディプロイ**: Agent Engineへのディプロイ（WIP）

---

## コントリビュート

自分のオリジナルのエージェントを作って、ぜひPRを作成して共有してください！

詳細は [CONTRIBUTING.md](CONTRIBUTING.md) をご確認ください。

### コントリビュート手順

1. このリポジトリをFork
2. Forkしたリポジトリをclone
3. [セットアップ手順](docs/setup_and_execution.md)に従ってエージェントを作成
4. PRを作成

---

## Web UI

ブラウザからチャット形式でエージェントを操作できます。手順は [セットアップと実行ガイド](docs/setup_and_execution.md#ブラウザでチャットa4a-web-ui) を参照してください。

- リアルタイムストリーミングで回答を表示
- どのサブエージェントが応答しているかバッジで確認可能
- マークダウン形式でレンダリング

---

## A2A実行例

複数のエージェントを連携させて実行できます。

```bash
# すべてのエージェントとコーディネーターを起動
make run

# 別ターミナルからクエリを送信
make query q="沖縄そば食べたい！"
make query q="ヤシの木について教えて"
make query q="新しいエージェントを作って"
```

詳細は [A2Aガイド](docs/a2a_guide.md) をご覧ください。

### 各エージェントを別ターミナルで起動する

各エージェントのログを分けて確認したい場合は、以下のコマンドをそれぞれ別ターミナルで実行してください。**プロジェクトルート（A4A）で実行**してください。

- 各エージェントを別ターミナルで起動し、**Coordinator（8000）だけ**にクエリを送ると、リクエスト／レスポンスのログや作業内容が**各エージェントのターミナル**に表示されます。
- 各エージェントの作業内容は **Coordinator が応答の末尾で報告**します（`[エージェント活動] エージェント名: 実施したこと, ...`）。

クエリの送り方: `make query q="質問"` または `adk web` で http://127.0.0.1:8000 のチャットへ入力。

コマンド一覧の再取得: `uv run python -m a4a.print_terminals`（`--powershell` または `--bash` で書式を指定可能）

**--- Coordinator (port 8000) ---**

```powershell
$env:PORT="8000"; uv run python -m a4a.agent
```

**--- サブエージェント（ポート 8001 から）---**

| エージェント | ポート | 起動コマンド |
|-------------|--------|---------------|
| agent_4_agent | 8001 | `$env:PORT="8001"; uv run python -m agent_4_agent.a2a_agent` |
| angel_agent | 8002 | `$env:PORT="8002"; uv run python -m angel_agent.a2a_agent` |
| animal_sound_guide | 8003 | `$env:PORT="8003"; uv run python -m animal_sound_guide.a2a_agent` |
| architect_agent | 8004 | `$env:PORT="8004"; uv run python -m architect_agent.a2a_agent` |
| engineer_agent | 8005 | `$env:PORT="8005"; uv run python -m engineer_agent.a2a_agent` |
| nago_chuka_route_agent | 8006 | `$env:PORT="8006"; uv run python -m nago_chuka_route_agent.a2a_agent` |
| okinawa_beach_recommender | 8007 | `$env:PORT="8007"; uv run python -m okinawa_beach_recommender.a2a_agent` |
| okinawa_express_bus_agent | 8008 | `$env:PORT="8008"; uv run python -m okinawa_express_bus_agent.a2a_agent` |
| okinawa_soba_recipe_agent | 8009 | `$env:PORT="8009"; uv run python -m okinawa_soba_recipe_agent.a2a_agent` |
| okinawa_soba_recommender | 8010 | `$env:PORT="8010"; uv run python -m okinawa_soba_recommender.a2a_agent` |
| okinawa_soba_search_agent | 8011 | `$env:PORT="8011"; uv run python -m okinawa_soba_search_agent.a2a_agent` |
| ops_agent | 8012 | `$env:PORT="8012"; uv run python -m ops_agent.a2a_agent` |
| palm_tree_info_agent | 8013 | `$env:PORT="8013"; uv run python -m palm_tree_info_agent.a2a_agent` |
| planning_agent | 8014 | `$env:PORT="8014"; uv run python -m planning_agent.a2a_agent` |
| planning_b_agent | 8015 | `$env:PORT="8015"; uv run python -m planning_b_agent.a2a_agent` |
| prompt_engineer_agent | 8016 | `$env:PORT="8016"; uv run python -m prompt_engineer_agent.a2a_agent` |
| review_agent | 8017 | `$env:PORT="8017"; uv run python -m review_agent.a2a_agent` |
| security_officer_agent | 8018 | `$env:PORT="8018"; uv run python -m security_officer_agent.a2a_agent` |

上記をそれぞれ別ターミナルにコピーして実行すると、各エージェントのログを分けて確認できます。ポートの並びは discovery の並び順に依存します。最新の一覧は `uv run python -m a4a.print_terminals` で確認してください。

---

## 参考リンク

- [ADK Python](https://github.com/google/adk-python)
- [ADK Documentation](https://google.github.io/adk-docs/)
- [A2A Protocol](https://codelabs.developers.google.com/intro-a2a-purchasing-concierge)
- [Vertex AI Agent Engine](https://docs.cloud.google.com/agent-builder/agent-engine/overview)

