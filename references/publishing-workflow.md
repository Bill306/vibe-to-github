# Publishing workflow

Use this reference for command-level execution after reading `SKILL.md`.

## 1. Inspect without mutation

```bash
pwd
git rev-parse --show-toplevel
git status --short --branch
git remote -v
git branch --show-current
find . -maxdepth 2 -type f
```

Adapt commands to the project and avoid printing environment files or credential contents. Identify the build system from manifests and lockfiles. Prefer `rg --files` for discovery. Verify commands against `package.json`, `pyproject.toml`, `Makefile`, CI, or existing documentation.

## 2. Prepare locally

Create or improve only the files required for a trustworthy repository. Typical additions are:

- `README.md`
- `.gitignore`
- `LICENSE` after confirmation
- `.env.example` containing names and safe placeholders only
- `CONTRIBUTING.md` or `SECURITY.md` only when the project needs them

Do not copy the real `.env` into `.env.example`. Do not remove files on the user's behalf. Report candidates for removal or relocation and request approval.

## 3. Validate

Run the bundled checks from the Skill directory:

```bash
python3 scripts/preflight.py /absolute/project/path --history
python3 scripts/detect_version.py /absolute/project/path
python3 scripts/validate_readme.py /absolute/project/path
```

Then run repository-native checks. Examples, only when present:

```bash
npm run lint
npm run typecheck
npm test
npm run build
python -m pytest
```

Record exact outcomes. A build proves buildability in the current environment, not production correctness.

## 4. Present the manifest

Use this shape:

```text
Project: /absolute/path
Remote action: create owner/name | update verified origin
Visibility: public | private | internal
Branch: main
License: SPDX identifier or All Rights Reserved
Current version: detected value and canonical source
Release version: exact user-confirmed value
Version actions: edit | commit | tag | push tag | GitHub Release | package publish
Files: explicit path list
README: PASS | WARNING | BLOCKED
Security: PASS | WARNING | BLOCKED
History coverage: gitleaks | filename-only heuristic | unavailable
Verification: command -> exit status -> claim supported
Known gaps: explicit list
```

Obtain confirmation before continuing.

## 5. Publish after confirmation

For a new isolated repository, initialize Git only at the confirmed project root. Stage explicit paths rather than the entire dirty parent workspace.

For GitHub CLI, first check authentication and target ownership. Use the visibility the user confirmed. Do not initialize a GitHub repository with extra README, ignore, or license options when pushing an existing local history because that can create an avoidable merge conflict.

Never replace an existing remote automatically. Never use `--force` or rewrite history as a normal publishing step. Do not create a tag, GitHub Release, or registry publication unless the manifest authorizes that exact action.

## 6. Verify remotely

Verify at least the URL, owner/name, visibility, default branch, expected commit and files, README rendering, license detection, and confirmed version source. Verify the tag and GitHub Release only when they were requested. If a secret is found after publication, prioritize credential rotation or revocation. Removing it from the latest tree does not remove it from history or copies.
