# vibe-to-github

**English** | [简体中文](README.zh-CN.md)

`vibe-to-github` is a Codex Skill for turning a local vibe-coded project into a GitHub repository that another person can understand, run, and trust.

## Problem

Vibe-coded projects often work on the creator's machine but reach GitHub with an inaccurate README, unclear setup steps, accidental credentials, private data, local paths, generated files, or an unconsidered license. This Skill makes those checks part of the publishing workflow and separates local preparation from remote authorization.

## Features

- **Three operating modes** — Review without edits, Prepare locally, or Publish after an explicit remote-action confirmation.
- **README contract** — Requires the problem, main features, installation, usage, and a realistic input/output example.
- **Adaptive formatting** — Selects an App/Product, Library/CLI, or Community/Content template instead of forcing one layout onto every project.
- **License decision gate** — Explains common software and content choices, checks third-party boundaries, and asks the user to confirm.
- **Read-only preflight** — Reports possible secrets, private data, local paths, artifacts, large files, risky Git history, and remote credentials without printing matched values.
- **Publication manifest** — Shows visibility, repository target, changed files, license, safety coverage, and verification evidence before any remote mutation.
- **Narrow Git behavior** — Avoids force-push, history rewrites, remote replacement, inferred deployment, and broad staging in dirty workspaces.

## Installation

Copy this folder into a compatible Codex skills directory:

```bash
cp -R vibe-to-github ~/.codex/skills/vibe-to-github
```

The Skill's Python checks use only the standard library. Git is required for repository and history inspection. A separately installed `gitleaks` executable adds content-level history scanning; the Skill does not install it automatically.

## Usage

Invoke it with a local project path and the desired mode:

```text
Use $vibe-to-github to review /path/to/my-project without changing files.
```

```text
Use $vibe-to-github to prepare /path/to/my-project for GitHub, but do not publish it yet.
```

```text
Use $vibe-to-github to prepare this project and show me the publication manifest before creating a private GitHub repository.
```

Run the deterministic checks directly when needed:

```bash
python3 scripts/preflight.py /path/to/my-project --history
python3 scripts/validate_readme.py /path/to/my-project
```

## Input and Output Example

**Input**

```text
Prepare my Next.js prototype for GitHub. Do not publish it yet.
```

**Output**

```text
Status: BLOCKED
README: missing input/output example
Security: possible credential file at .env.local
History coverage: filename-only scan; gitleaks unavailable
Remote action: none performed
Next action: rotate any real exposed credential, create a sanitized .env.example,
and rerun the checks after the user approves the local changes.
```

The Skill reports filenames and finding types, not secret values.

## Repository Structure

```text
.
├── README.md
├── README.zh-CN.md
├── SKILL.md
├── agents/openai.yaml
├── assets/templates/
├── examples/
├── references/
├── scripts/
├── AGENTS.md
└── LICENSE
```

## Known Limitations

- Heuristic secret and privacy checks can produce false positives and false negatives.
- Full content-level Git-history scanning requires a compatible external scanner such as gitleaks.
- The README validator can check structure and some command consistency, but it cannot prove that prose accurately describes business behavior.
- License guidance is educational and is not legal advice.
- A successful build or push does not prove production correctness or security.

## Security and Privacy

The bundled scripts are read-only with respect to the target project. They do not delete files, rewrite Git history, upload data, install dependencies, or create GitHub repositories. Findings are redacted to filenames, categories, and approximate line numbers.

For a suspected real credential, rotate or revoke it before addressing repository history. See [references/security-checklist.md](references/security-checklist.md).

## Contributing

Keep checks conservative, outputs redacted, and authorization gates explicit. Run the repository validation before proposing changes:

```bash
scripts/validate.sh
```

## License

MIT License. See [LICENSE](LICENSE).
