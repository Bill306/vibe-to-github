---
name: vibe-to-github
description: Prepare and publish locally built or vibe-coded apps, libraries, CLIs, and content projects as trustworthy GitHub repositories. Use when a user asks to make a project GitHub-ready, write or improve its README, choose a license, detect or confirm a release version, audit secrets and private data, initialize Git safely, create a GitHub repository, or push an existing local project. Supports prepare-only and publish modes, with mandatory README, license, version, security, validation, visibility, and explicit remote-action gates.
---

# Vibe to GitHub

Turn a local project into a repository that another person can understand, run, and trust. Inspect before writing, report before publishing, and never treat a successful push as proof that the project works.

## Select the mode

- **Prepare:** Audit and improve the local project. Do not create or update a remote.
- **Publish:** Complete Prepare, then create or update a GitHub repository only after the user confirms the exact remote action.
- **Review:** Report readiness without changing project files or Git state.

If the request does not clearly authorize local edits, use Review. If it authorizes GitHub publication but omits visibility, account/organization, or target repository, prepare the project and ask for the missing remote decision before publishing.

## Follow the workflow

### 1. Establish the project boundary

1. Resolve the project root and check whether it is already inside a Git repository.
2. Inspect `git status`, remotes, branches, ignore rules, manifests, lockfiles, entry points, and existing documentation.
3. Preserve unrelated changes. Never operate from a dirty parent repository when the intended project can be isolated.
4. Ask for clarification when the project root or intended remote is ambiguous.

Do not delete user files, rewrite history, replace a remote, force-push, change repository visibility, or enable deployment as an inferred step.

### 2. Build an evidence-backed release brief

Derive these facts from the project, then ask only for facts that cannot be verified:

- Project name and one-sentence value proposition
- Intended users and problem solved
- Real features and known limitations
- Supported runtime, installation, and start commands
- Input and output examples
- Project type: App/Product, Library/CLI, or Community/Content
- Existing deployment URL and screenshots, if real
- Declared version sources and existing Git tags
- Proposed repository name, owner, visibility, and license

Never invent a feature, command, screenshot, compatibility claim, benchmark, test result, or badge status.

### 3. Run the safety gate

Read [references/security-checklist.md](references/security-checklist.md), then run:

```bash
python3 scripts/preflight.py /absolute/path/to/project --history
```

Interpret results as:

- `PASS`: no detected blocker; continue.
- `WARNING`: explain each uncertainty and obtain explicit acknowledgement before public publication.
- `BLOCKED`: stop publication. Explain remediation without exposing secret values.

Treat a heuristic scan as one layer, not a guarantee. If a real credential may have been committed, instruct the user to rotate or revoke it; deleting the file is not sufficient. Do not install scanners, remove files, or rewrite Git history without action-specific approval.

### 4. Choose and confirm the license

Read [references/license-guide.md](references/license-guide.md). Recommend rather than silently select:

- MIT for simple permissive software reuse.
- Apache-2.0 when an explicit patent grant matters.
- GPL-3.0 for reciprocal distribution of modified software.
- AGPL-3.0 when reciprocal obligations should include network use.
- A suitable Creative Commons license for standalone content or datasets, not software code.
- No open-source license when the user wants all rights reserved.

Check third-party code, fonts, images, models, and datasets separately. Ask the user to confirm the final choice and copyright holder. Do not provide legal certainty.

### 5. Detect and confirm the version

Read [references/versioning-guide.md](references/versioning-guide.md), then run:

```bash
python3 scripts/detect_version.py /absolute/path/to/project
```

Report every detected version source and the latest semantic Git tag. If sources disagree, stop and ask which source is canonical. If no version exists, ask whether this is an experimental first release or a stable public release; do not silently choose `0.1.0` or `1.0.0`.

Always ask the user to confirm both the detected current version and the exact intended release version. When the user chooses Patch, Minor, Major, or Prerelease, show the resulting version number before editing files.

Treat these as separate actions: edit version files, commit the change, create a tag, push a tag, create a GitHub Release, and publish a package. Do not infer one authorization from another.

### 6. Create or repair the README

Read [references/readme-patterns.md](references/readme-patterns.md) and select the matching template under `assets/templates/`.

Every project README must accurately cover:

1. What problem the project solves
2. Main features
3. Installation
4. Usage
5. A concrete input/output example

Prefer this user-first order when applicable: project name, one-sentence value, verified badges, demo or real screenshot, features, Quick Start, installation, configuration, usage, input/output, limitations, security, contributing, license.

Validate it with:

```bash
python3 scripts/validate_readme.py /absolute/path/to/project
```

Resolve every `BLOCKED` finding. A `WARNING` must be explained, not hidden.

### 7. Verify the project

Infer verification commands from repository evidence, such as manifest scripts, documented commands, or existing CI. Prefer the smallest relevant sequence: formatting or lint, typecheck, tests, build, then a smoke check when safe.

Do not invent missing commands. Do not start long-running services without a bounded check. Record the exact command, exit status, and what it actually proves. Report unavailable or failing verification as `PARTIAL` or `BLOCKED` according to impact.

### 8. Present the publication manifest

Before any remote mutation, show:

- Absolute project path
- GitHub owner and repository name
- Create-new or update-existing action
- Public, private, or internal visibility
- Default branch and existing remote, if any
- Files to add or change
- README validation result
- License choice and copyright holder
- Detected current version, source of truth, confirmed release version, and authorized version/tag/release actions
- Safety result, including history-scan coverage
- Test/build/smoke results and known gaps
- Exact GitHub action proposed

Ask for explicit confirmation of this manifest. A prior general request to "put it on GitHub" does not authorize an unspecified public repository, remote replacement, history rewrite, or visibility change.

### 9. Publish narrowly

After confirmation:

1. Re-run the safety check against the final working tree and staged diff.
2. Apply the exact confirmed version change only when authorized, then rerun relevant validation.
3. Stage explicit approved paths. Avoid `git add -A` when unrelated files exist.
4. Create a normal commit with an accurate message.
5. Use the confirmed owner, repository name, and visibility.
6. If a remote already exists, verify it instead of replacing it.
7. Push without force.

Create or push a Git tag, GitHub Release, or package only when each action appears in the confirmed manifest.

Do not enable GitHub Pages, Actions secrets, Vercel, releases, packages, or collaborator access unless separately requested.

### 10. Verify the remote outcome

Confirm the repository URL, visibility, default branch, commit, README rendering, license detection, version source, and expected files. Verify tags or releases only when they were explicitly requested. If possible, verify cloneability from a clean temporary location. Distinguish:

- `READY`: local checks and remote verification passed.
- `PARTIAL`: publication succeeded but named checks are missing or failing.
- `BLOCKED`: publication was not performed or cannot safely proceed.

Return the repository link only when it was actually verified.

## Use the bundled resources

- [references/publishing-workflow.md](references/publishing-workflow.md): command-level prepare and publish procedure.
- [references/readme-patterns.md](references/readme-patterns.md): project-type templates and formatting rules learned from strong GitHub READMEs.
- [references/license-guide.md](references/license-guide.md): license decision guide and confirmation questions.
- [references/versioning-guide.md](references/versioning-guide.md): version-source detection, SemVer choices, and separate tag/release authorization.
- [references/security-checklist.md](references/security-checklist.md): secret, privacy, path, artifact, history, and dependency checks.
- `scripts/preflight.py`: read-only heuristic project and Git-history audit.
- `scripts/detect_version.py`: read-only manifest and semantic Git-tag version detection.
- `scripts/validate_readme.py`: deterministic README structure and command-consistency checks.
- `assets/templates/`: adaptable README starting points; replace every placeholder with verified project facts.

## Preserve the authorization boundary

Local analysis is not remote authorization. GitHub publication is not deployment authorization. Public visibility is not implied by "share" or "publish." Never delete user data, expose detected secret values, or claim a repository is safe solely because the bundled scripts returned `PASS`.
