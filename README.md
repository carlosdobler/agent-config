# agent-config

Sync AI skills (markdown files + reference folders) from GitHub to your Gemini agent.

## New VM

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/carlosdobler/agent-config/main/bootstrap.sh)
```

Skills will be placed in `~/.agents/skills/`.

## Already set up

```bash
cd ~/agent-config && git pull
```

The post-merge hook re-syncs skills automatically.

## Adding a skill

1. Edit `skills-manifest.json`:

```json
{
  "skills": [
    {
      "repo": "owner/repo",
      "paths": ["path/to/skill-folder"],
      "dest": "my-skill-name"
    }
  ]
}
```

2. Commit, push, then `git pull` on each VM.

## Manual sync

```bash
cd ~/agent-config
python3 sync_skills.py                         # default ~/.agents/skills
python3 sync_skills.py --dest ~/other/path     # custom destination
python3 sync_skills.py --dry-run               # preview without writing
```

## Files

| File | Purpose |
|---|---|
| `skills-manifest.json` | Source of truth — which skills to pull |
| `sync_skills.py` | Fetches skills from GitHub (no dependencies) |
| `bootstrap.sh` | One-command setup for a new VM |
| `hooks/post-merge` | Git hook: auto-sync on `git pull` |
