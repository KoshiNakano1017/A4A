import subprocess
import sys
import time
import os
import signal
import threading
from pathlib import Path

from dotenv import load_dotenv

from .discovery import discover_agents

# .env を読み込み（OUTPUT_PROJECT_ROOT 等）。プロジェクトルートと agent_4_agent の両方を試す
_root = Path(__file__).resolve().parent.parent
load_dotenv(_root / ".env")
load_dotenv(_root / "agent_4_agent" / ".env")

VERBOSE_FLAG = "--verbose"
VERBOSE_SHORT = "-v"


def _stream_output(pipe, prefix: str):
    """サブプロセスの stdout を読み、行ごとに [prefix] を付けて表示する。"""
    try:
        for line in iter(pipe.readline, ""):
            if line:
                sys.stdout.write(f"[{prefix}] {line}")
                sys.stdout.flush()
    except (BrokenPipeError, OSError):
        pass
    finally:
        try:
            pipe.close()
        except OSError:
            pass


def main():
    verbose = VERBOSE_FLAG in sys.argv or VERBOSE_SHORT in sys.argv
    # (process, name) のリスト。cleanup で process だけ参照する
    process_list = []

    def cleanup(signum, frame):
        print("\nStopping all agents...")
        for p, _ in process_list:
            if p.poll() is None:
                p.terminate()
        time.sleep(1)
        for p, _ in process_list:
            if p.poll() is None:
                p.kill()
        sys.exit(0)

    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)

    try:
        print("Discovering agents...")
        agents = discover_agents()

        for agent in agents:
            env = os.environ.copy()
            env["PORT"] = str(agent.port)

            if verbose:
                p = subprocess.Popen(
                    [sys.executable, "-m", agent.module],
                    env=env,
                    cwd=os.getcwd(),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    bufsize=1,
                )
                t = threading.Thread(
                    target=_stream_output,
                    args=(p.stdout, f"{agent.name}:{agent.port}"),
                    daemon=True,
                )
                t.start()
                print(f"Started {agent.name} on port {agent.port} (verbose)")
            else:
                p = subprocess.Popen(
                    [sys.executable, "-m", agent.module],
                    env=env,
                    cwd=os.getcwd(),
                )
                print(f"Started {agent.name} on port {agent.port}")

            process_list.append((p, agent.name))

        # Coordinator
        env_coord = os.environ.copy()
        env_coord["PORT"] = "8000"
        if verbose:
            p_coord = subprocess.Popen(
                [sys.executable, "-m", "a4a.agent"],
                env=env_coord,
                cwd=os.getcwd(),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                bufsize=1,
            )
            t_coord = threading.Thread(
                target=_stream_output,
                args=(p_coord.stdout, "coordinator:8000"),
                daemon=True,
            )
            t_coord.start()
            print("Started coordinator_agent on port 8000 (verbose)")
        else:
            p_coord = subprocess.Popen(
                [sys.executable, "-m", "a4a.agent"],
                env=env_coord,
                cwd=os.getcwd(),
            )
            print("Started coordinator_agent on port 8000")

        process_list.append((p_coord, "coordinator"))

        if verbose:
            print("\n--- 各エージェントのログは [エージェント名:ポート] プレフィックス付きで表示されます。Ctrl+C で終了。---\n")

        while True:
            time.sleep(1)
            dead = [(p, name) for p, name in process_list if p.poll() is not None]
            for p, name in dead:
                print(f"Process {name} exited with code {p.returncode}")
                process_list.remove((p, name))
    except Exception as e:
        print(f"Error: {e}")
        cleanup(None, None)


if __name__ == "__main__":
    main()
