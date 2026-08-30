# Agent instructions

1. Preserve the three modes: Review, Prepare, and Publish.
2. Never delete user data, expose matched secret values, force-push, rewrite history, replace a remote, or infer public visibility.
3. Keep `SKILL.md` concise and execution-oriented; put detailed rules in `references/` and reusable output starters in `assets/templates/`.
4. Keep scanner output redacted. Report filenames, line numbers, and finding types only.
5. Require the README content contract: problem, features, installation, usage, and input/output example.
6. Detect and confirm the current and release versions; never infer authorization to edit manifests, create tags, create GitHub Releases, or publish packages.
7. Treat scripts as heuristic checks, not proof of safety or functional correctness.
8. Run `scripts/validate.sh` before committing or packaging changes.
