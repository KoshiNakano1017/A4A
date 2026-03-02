# https://google.github.io/adk-docs/a2a/quickstart-exposing/#exposing-the-remote-agent-with-the-to_a2aroot_agent-function
from . import root_agent

if __name__ == "__main__":
    from a4a.agent_activity import run_a2a_with_activity
    run_a2a_with_activity(root_agent)
