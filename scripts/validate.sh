#!/usr/bin/env bash
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

required=(
  SKILL.md README.md README.zh-CN.md LICENSE AGENTS.md agents/openai.yaml
  references/publishing-workflow.md references/readme-patterns.md
  references/license-guide.md references/security-checklist.md
  assets/templates/app-product.md assets/templates/library-cli.md
  assets/templates/community-content.md scripts/preflight.py
  scripts/validate_readme.py scripts/test_checks.py
)

for relative in "${required[@]}"; do
  test -f "$SKILL_DIR/$relative" || { echo "missing $relative" >&2; exit 1; }
done

grep -Fq 'default_prompt: "Use $vibe-to-github' "$SKILL_DIR/agents/openai.yaml"
grep -Fq 'name: vibe-to-github' "$SKILL_DIR/SKILL.md"
grep -Fq '[简体中文](README.zh-CN.md)' "$SKILL_DIR/README.md"
grep -Fq '[English](README.md)' "$SKILL_DIR/README.zh-CN.md"

python3 -m py_compile \
  "$SKILL_DIR/scripts/preflight.py" \
  "$SKILL_DIR/scripts/validate_readme.py" \
  "$SKILL_DIR/scripts/test_checks.py"

python3 "$SKILL_DIR/scripts/test_checks.py"
python3 "$SKILL_DIR/scripts/validate_readme.py" "$SKILL_DIR" --type library-cli
python3 "$SKILL_DIR/scripts/validate_readme.py" "$SKILL_DIR/README.zh-CN.md" --type library-cli

echo "vibe-to-github repository validation passed"
