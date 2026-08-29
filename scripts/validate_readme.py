#!/usr/bin/env python3
"""Validate a project README against the vibe-to-github content contract."""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
from pathlib import Path
import re
import shlex
from typing import Iterable


SECTION_ALIASES = {
    "problem": ("problem", "overview", "about", "why", "introduction", "简介", "项目介绍", "解决什么问题", "问题"),
    "features": ("features", "capabilities", "what it does", "主要功能", "功能", "能做什么"),
    "installation": ("installation", "install", "setup", "getting started", "安装", "环境准备"),
    "usage": ("usage", "quick start", "how to use", "run", "使用", "快速开始", "运行"),
    "input_output": ("input and output", "input/output", "example", "examples", "输入输出", "输入与输出", "示例"),
    "license": ("license", "licence", "许可证", "授权"),
}

PLACEHOLDERS = [
    re.compile(r"(?i)\bTODO\b"),
    re.compile(r"(?i)\bTBD\b"),
    re.compile(r"(?i)your[-_ ]project"),
    re.compile(r"\{\{[^}]+\}\}"),
    re.compile(r"(?i)<project[-_ ]?(?:name|description)>"),
]

HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$", re.MULTILINE)
CODE_BLOCK_RE = re.compile(r"```[^\n]*\n(.*?)```", re.DOTALL)
IMAGE_RE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
BADGE_RE = re.compile(r"!\[[^\]]*\]\([^)]*(?:shields\.io|badge|actions/workflows)[^)]*\)", re.IGNORECASE)


@dataclass(frozen=True)
class Finding:
    severity: str
    category: str
    detail: str


def normalized_heading(value: str) -> str:
    value = re.sub(r"<[^>]+>", "", value)
    value = re.sub(r"[`*_~]", "", value)
    return value.strip().casefold()


def has_section(headings: list[str], aliases: Iterable[str]) -> bool:
    for heading in headings:
        for alias in aliases:
            if alias.casefold() in heading:
                return True
    return False


def section_body(text: str, aliases: Iterable[str]) -> str:
    matches = list(HEADING_RE.finditer(text))
    for index, match in enumerate(matches):
        heading = normalized_heading(match.group(2))
        if not any(alias.casefold() in heading for alias in aliases):
            continue
        level = len(match.group(1))
        end = len(text)
        for following in matches[index + 1:]:
            if len(following.group(1)) <= level:
                end = following.start()
                break
        return text[match.end():end]
    return ""


def detect_project_type(root: Path) -> str:
    package = root / "package.json"
    if package.is_file():
        try:
            data = json.loads(package.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            data = {}
        dependencies = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
        if any(name in dependencies for name in ("next", "react", "vue", "svelte", "@angular/core")):
            return "app"
        return "library-cli"
    if any((root / name).is_file() for name in ("pyproject.toml", "setup.py", "Cargo.toml", "go.mod")):
        return "library-cli"
    code_extensions = {".py", ".js", ".ts", ".tsx", ".jsx", ".go", ".rs", ".java"}
    if any(path.suffix.lower() in code_extensions for path in root.rglob("*") if path.is_file() and ".git" not in path.parts):
        return "app"
    return "community-content"


def load_package_scripts(root: Path) -> dict[str, str]:
    package = root / "package.json"
    if not package.is_file():
        return {}
    try:
        data = json.loads(package.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    scripts = data.get("scripts", {})
    return scripts if isinstance(scripts, dict) else {}


def validate_commands(root: Path, text: str) -> list[Finding]:
    findings: list[Finding] = []
    scripts = load_package_scripts(root)
    blocks = CODE_BLOCK_RE.findall(text)
    commands = "\n".join(blocks)

    for script in re.findall(r"\bnpm\s+run\s+([\w:.-]+)", commands):
        if scripts and script not in scripts:
            findings.append(Finding("BLOCKED", "command consistency", f"README uses `npm run {script}` but package.json has no `{script}` script"))
    for script in re.findall(r"\bpnpm\s+(?!install\b|add\b|exec\b|dlx\b)([\w:.-]+)", commands):
        if scripts and script not in scripts:
            findings.append(Finding("BLOCKED", "command consistency", f"README uses `pnpm {script}` but package.json has no `{script}` script"))
    for script in re.findall(r"\byarn\s+(?!install\b|add\b|dlx\b)([\w:.-]+)", commands):
        if scripts and script not in scripts:
            findings.append(Finding("BLOCKED", "command consistency", f"README uses `yarn {script}` but package.json has no `{script}` script"))

    for block in blocks:
        for raw in block.splitlines():
            line = raw.strip()
            if not line or line.startswith(("#", "$")):
                continue
            try:
                tokens = shlex.split(line)
            except ValueError:
                continue
            if len(tokens) >= 2 and tokens[0] in {"python", "python3"} and tokens[1] != "-m" and tokens[1].endswith(".py"):
                referenced = (root / tokens[1]).resolve()
                try:
                    referenced.relative_to(root)
                except ValueError:
                    continue
                if not referenced.is_file():
                    findings.append(Finding("BLOCKED", "command consistency", f"README references missing script `{tokens[1]}`"))
    return findings


def dedupe(findings: Iterable[Finding]) -> list[Finding]:
    return sorted(set(findings), key=lambda item: ({"BLOCKED": 0, "WARNING": 1}.get(item.severity, 2), item.category, item.detail))


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a GitHub README")
    parser.add_argument("project", help="Project directory or README path")
    parser.add_argument("--type", choices=("auto", "app", "library-cli", "community-content"), default="auto")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()

    supplied = Path(args.project).expanduser().resolve()
    if supplied.is_dir():
        root, readme = supplied, supplied / "README.md"
    else:
        root, readme = supplied.parent, supplied

    findings: list[Finding] = []
    if not readme.is_file():
        findings.append(Finding("BLOCKED", "README", "root README.md is missing"))
        text = ""
    else:
        text = readme.read_text(encoding="utf-8", errors="replace")

    if text:
        size = len(text.encode("utf-8"))
        if size > 500 * 1024:
            findings.append(Finding("BLOCKED", "README size", "README exceeds GitHub's 500 KiB rendered-content limit"))
        elif size > 100 * 1024:
            findings.append(Finding("WARNING", "README size", "README is over 100 KiB; consider progressive disclosure"))

        headings = [normalized_heading(match.group(2)) for match in HEADING_RE.finditer(text)]
        h1_count = sum(1 for match in HEADING_RE.finditer(text) if len(match.group(1)) == 1)
        if h1_count != 1:
            findings.append(Finding("WARNING", "heading hierarchy", f"expected one H1 project title, found {h1_count}"))

        for key, aliases in SECTION_ALIASES.items():
            if not has_section(headings, aliases):
                findings.append(Finding("BLOCKED", "required section", f"missing section for {key.replace('_', ' ')}"))

        for pattern in PLACEHOLDERS:
            if pattern.search(text):
                findings.append(Finding("BLOCKED", "placeholder", f"unresolved placeholder matches `{pattern.pattern}`"))

        for alt, target in IMAGE_RE.findall(text):
            if not alt.strip():
                findings.append(Finding("WARNING", "image accessibility", f"image `{target}` has empty alt text"))
            if target.startswith("/") and not target.startswith("//"):
                findings.append(Finding("WARNING", "image portability", f"image `{target}` uses an absolute path"))

        badge_count = len(BADGE_RE.findall(text))
        if badge_count > 6:
            findings.append(Finding("WARNING", "badges", f"README contains {badge_count} badges; keep only decision-useful verified badges"))

        if not CODE_BLOCK_RE.search(text):
            findings.append(Finding("WARNING", "runnable documentation", "README contains no fenced command or code example"))

        project_type = detect_project_type(root) if args.type == "auto" else args.type
        if project_type == "app" and not IMAGE_RE.search(text) and not re.search(r"(?i)\b(?:live\s+demo|demo\s*[:：]|预览|在线体验)\b", text):
            findings.append(Finding("WARNING", "product evidence", "app README has neither a real screenshot nor a demo entry"))
        if project_type == "library-cli" and len(CODE_BLOCK_RE.findall(text)) < 2:
            findings.append(Finding("WARNING", "minimum example", "library/CLI README should normally include installation and usage code blocks"))

        if not has_section(headings, ("limitations", "known issues", "已知限制", "限制")):
            findings.append(Finding("WARNING", "limitations", "known limitations are not stated"))
        if not has_section(headings, ("security", "privacy", "安全", "隐私")):
            findings.append(Finding("WARNING", "security", "security or privacy handling is not stated"))

        license_body = section_body(text, SECTION_ALIASES["license"])
        license_file = next((root / name for name in ("LICENSE", "LICENSE.md", "LICENSE.txt") if (root / name).is_file()), None)
        all_rights_reserved = bool(re.search(r"(?i)(all rights reserved|no open[- ]source license|保留所有权利|未采用开源许可证)", license_body))
        if license_file is None and not all_rights_reserved:
            findings.append(Finding("BLOCKED", "license", "README does not link to a license file or explicitly state that no open-source license is granted"))

        findings.extend(validate_commands(root, text))
    else:
        project_type = detect_project_type(root) if root.is_dir() else "unknown"

    findings = dedupe(findings)
    status = "BLOCKED" if any(item.severity == "BLOCKED" for item in findings) else "WARNING" if findings else "PASS"
    payload = {
        "status": status,
        "readme": str(readme),
        "project_type": project_type,
        "findings": [asdict(item) for item in findings],
    }

    if args.as_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"{status}: {readme}")
        print(f"Project type: {project_type}")
        for item in findings:
            print(f"[{item.severity}] {item.category}: {item.detail}")

    return 2 if status == "BLOCKED" else 1 if status == "WARNING" else 0


if __name__ == "__main__":
    raise SystemExit(main())
