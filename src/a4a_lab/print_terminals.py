"""
各エージェントを別ターミナルで起動するためのコマンドを表示します。
discovery と同じ並び順・ポートで出力するので、コピペでそのまま使えます。

使い方:
  uv run python -m a4a_lab.print_terminals
  uv run python -m a4a_lab.print_terminals --powershell   # PowerShell のみ
  uv run python -m a4a_lab.print_terminals --bash         # bash のみ
"""
import sys
from .discovery import discover_agents


def main():
    agents = discover_agents()
    show_powershell = "--bash" not in sys.argv
    show_bash = "--powershell" not in sys.argv
    if "--powershell" in sys.argv:
        show_bash = False
    if "--bash" in sys.argv:
        show_powershell = False

    lines = [
        "",
        "各エージェントを別ターミナルで起動するコマンド（discovery の並び順）",
        "Coordinator はプロジェクトルート（A4A）で実行してください。",
        "サブエージェントは `agents/` ディレクトリ内で実行してください。",
        "",
    ]

    # Coordinator
    lines.append("--- Coordinator (port 8000) ---")
    if show_powershell:
        lines.append('  $env:PORT="8000"; uv run python -m a4a_lab.agent')
    if show_bash:
        lines.append("  PORT=8000 uv run python -m a4a_lab.agent")
    lines.append("")

    # Sub-agents
    lines.append("--- サブエージェント（ポート 8001 から）---")
    for a in agents:
        lines.append(f"  {a.name}  (port {a.port})")
        if show_powershell:
            lines.append(f'  cd agents; $env:PORT="{a.port}"; uv run python -m {a.module}')
        if show_bash:
            lines.append(f"  cd agents && PORT={a.port} uv run python -m {a.module}")
        lines.append("")

    lines.append("---")
    lines.append("上記をそれぞれ別ターミナルにコピーして実行すると、各エージェントのログを分けて確認できます。")
    lines.append("")

    print("\n".join(lines))


if __name__ == "__main__":
    main()
