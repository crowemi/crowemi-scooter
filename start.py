#!/usr/bin/env python3

import json
import os
import re
import subprocess
from pathlib import Path


def run(command: list[str]) -> int:
    result = subprocess.run(command, check=False)
    return result.returncode


def start_ssh_agent() -> None:
    result = subprocess.run(["ssh-agent", "-s"], capture_output=True, text=True, check=False)
    if result.returncode != 0:
        return

    for key, value in re.findall(r"(SSH_AUTH_SOCK|SSH_AGENT_PID)=([^;\n]+)", result.stdout):
        os.environ[key] = value


def configure_git_identity(config_path: Path) -> None:
    if not config_path.exists():
        return

    try:
        with config_path.open("r", encoding="utf-8") as file_handle:
            config = json.load(file_handle)
    except (OSError, json.JSONDecodeError):
        return

    user_config = config.get("user", {}) if isinstance(config, dict) else {}
    github_config = config.get("github", {}) if isinstance(config, dict) else {}

    name = (
        config.get("name")
        or config.get("user.name")
        or user_config.get("name")
        or github_config.get("name")
    )
    email = (
        config.get("email")
        or config.get("user.email")
        or user_config.get("email")
        or github_config.get("email")
    )

    if isinstance(name, str) and name.strip():
        run(["git", "config", "--global", "user.name", name.strip()])

    if isinstance(email, str) and email.strip():
        run(["git", "config", "--global", "user.email", email.strip()])


def main() -> int:
    start_ssh_agent()
    configure_git_identity(Path("/openclaw/data/config/.github/config.json"))

    run(["ssh-add", "/openclaw/data/config/.ssh/github"])
    run(["ssh-add", "-l"])

    root_ssh = Path("/root/.ssh")
    root_ssh.mkdir(parents=True, exist_ok=True)
    known_hosts = root_ssh / "known_hosts"
    known_hosts.touch(exist_ok=True)

    with known_hosts.open("a", encoding="utf-8") as file_handle:
        subprocess.run(["ssh-keyscan", "-H", "github.com"], stdout=file_handle, stderr=subprocess.DEVNULL, check=False)

    run(["ssh", "-T", "git@github.com"])

    return run(["openclaw", "gateway", "--port", "18789"])


if __name__ == "__main__":
    raise SystemExit(main())