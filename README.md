## OpenClaw Docker Setup

This project runs OpenClaw in Docker and reads local secret config files from `./data/config`.

### Where to put secret config files

Create these files on your host machine:

- `data/config/.ssh/github` (GitHub SSH private key)
- `data/config/.github/config.json` (Git identity config)

The container mounts this directory to `/openclaw/data/config`, so inside the container the files are read from:

- `/openclaw/data/config/.ssh/github`
- `/openclaw/data/config/.github/config.json`

### Required directory structure

```text
data/
	config/
		.ssh/
			github
		.github/
			config.json
```

### SSH key setup

1. Put your GitHub private key in `data/config/.ssh/github`.
2. Restrict permissions:

```bash
chmod 700 data/config/.ssh
chmod 600 data/config/.ssh/github
```

At startup, the container runs `ssh-agent`, adds this key, and adds `github.com` to known hosts.

### GitHub identity config (`config.json`)

Put your Git author identity in `data/config/.github/config.json`.

Example:

```json
{
	"name": "Your Name",
	"email": "you@example.com"
}
```

Supported keys are:

- top-level `name` + `email`
- top-level `user.name` + `user.email`
- nested `user.name` + `user.email`
- nested `github.name` + `github.email`

On startup, these values are applied with global git config:

- `git config --global user.name ...`
- `git config --global user.email ...`

### Run

```bash
docker compose up --build
```
