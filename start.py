#!/usr/bin/env python3

import json
import os
import re
import shutil
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

    name = config.get("name")
    email = config.get("email")

    if isinstance(name, str) and name.strip():
        run(["git", "config", "--global", "user.name", name.strip()])

    if isinstance(email, str) and email.strip():
        run(["git", "config", "--global", "user.email", email.strip()])

    pat = config.get("pat") if isinstance(config, dict) else None
    if isinstance(pat, str) and pat.strip():
        token = pat.strip()
        os.environ["GH_TOKEN"] = token
        # Persist auth in gh's own config
        subprocess.run(
            ["gh", "auth", "login", "--with-token"],
            input=token,
            text=True,
            check=False,
        )
        run(["gh", "auth", "setup-git"])

        # Write token to git credential store so HTTPS pushes work non-interactively
        credentials_path = Path.home() / ".git-credentials"
        credentials_path.write_text(
            f"https://x-access-token:{token}@github.com\n", encoding="utf-8"
        )
        credentials_path.chmod(0o600)
        run(["git", "config", "--global", "credential.helper", "store"])
        print("GitHub PAT configured (gh auth + git credential store).")


def configure_notion_api_key(config_path: Path) -> None:
    if not config_path.exists():
        return

    try:
        with config_path.open("r", encoding="utf-8") as file_handle:
            config = json.load(file_handle)
    except (OSError, json.JSONDecodeError):
        return

    key = config.get("key") if isinstance(config, dict) else None
    if isinstance(key, str) and key.strip():
        os.environ["NOTION_API_KEY"] = key.strip()


def fix_config_permissions(config_dir: Path) -> None:
    """Ensure all directories under config have the execute bit so they are traversable."""
    if config_dir.is_dir():
        for root, dirs, files in os.walk(config_dir):
            root_path = Path(root)
            # Ensure the directory itself is accessible
            root_path.chmod(root_path.stat().st_mode | 0o755)
            for d in dirs:
                dirpath = root_path / d
                dirpath.chmod(dirpath.stat().st_mode | 0o755)
            for f in files:
                filepath = root_path / f
                # SSH private keys must stay 0600; set everything else to 0644
                if ".ssh" in root_path.parts:
                    filepath.chmod(0o600)
                else:
                    filepath.chmod(filepath.stat().st_mode | 0o644)


def main() -> int:
    os.umask(0o022)
    fix_config_permissions(Path("/openclaw/data/config"))
    start_ssh_agent()
    configure_git_identity(Path("/openclaw/data/config/.github/config.json"))
    configure_notion_api_key(Path("/openclaw/data/config/.notion/config.json"))

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