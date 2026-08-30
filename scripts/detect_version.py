#!/usr/bin/env python3
"""Detect declared project versions and the latest semantic Git tag."""

from __future__ import annotations

import argparse
import configparser
from dataclasses import asdict, dataclass
import json
from pathlib import Path
import re
import subprocess
import tomllib
from typing import Iterable


SEMVER_RE = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-((?:0|[1-9]\d*|\d*[A-Za-z-][0-9A-Za-z-]*)"
    r"(?:\.(?:0|[1-9]\d*|\d*[A-Za-z-][0-9A-Za-z-]*))*))?"
    r"(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$"
)


@dataclass(frozen=True)
class Candidate:
    source: str
    version: str
    semantic: bool


def normalize(value: object) -> str | None:
    if not isinstance(value, (str, int, float)):
        return None
    text = str(value).strip()
    return text or None


def add_candidate(candidates: list[Candidate], source: str, value: object) -> None:
    version = normalize(value)
    if version:
        candidates.append(Candidate(source, version, bool(SEMVER_RE.fullmatch(version))))


def read_json(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def read_toml(path: Path) -> dict:
    try:
        with path.open("rb") as handle:
            data = tomllib.load(handle)
    except (OSError, tomllib.TOMLDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def detect_declared(root: Path) -> list[Candidate]:
    candidates: list[Candidate] = []

    package = root / "package.json"
    if package.is_file():
        add_candidate(candidates, "package.json:version", read_json(package).get("version"))

    pyproject = root / "pyproject.toml"
    if pyproject.is_file():
        data = read_toml(pyproject)
        project = data.get("project", {}) if isinstance(data.get("project"), dict) else {}
        poetry = data.get("tool", {}).get("poetry", {}) if isinstance(data.get("tool"), dict) else {}
        add_candidate(candidates, "pyproject.toml:project.version", project.get("version"))
        if isinstance(poetry, dict):
            add_candidate(candidates, "pyproject.toml:tool.poetry.version", poetry.get("version"))

    cargo = root / "Cargo.toml"
    if cargo.is_file():
        data = read_toml(cargo)
        package_data = data.get("package", {}) if isinstance(data.get("package"), dict) else {}
        add_candidate(candidates, "Cargo.toml:package.version", package_data.get("version"))

    setup_cfg = root / "setup.cfg"
    if setup_cfg.is_file():
        parser = configparser.ConfigParser()
        try:
            parser.read(setup_cfg, encoding="utf-8")
            if parser.has_option("metadata", "version"):
                add_candidate(candidates, "setup.cfg:metadata.version", parser.get("metadata", "version"))
        except configparser.Error:
            pass

    for name in ("VERSION", "VERSION.txt", ".version"):
        path = root / name
        if not path.is_file():
            continue
        try:
            first_line = path.read_text(encoding="utf-8", errors="replace").splitlines()[0]
        except (OSError, IndexError):
            continue
        add_candidate(candidates, name, first_line)

    return candidates


def git_tags(root: Path) -> list[str]:
    result = subprocess.run(
        ["git", "-C", str(root), "tag", "--list", "--sort=-version:refname"],
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )
    if result.returncode != 0:
        return []
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def semantic_tag(tag: str) -> str | None:
    value = tag[1:] if tag.startswith("v") else tag
    return value if SEMVER_RE.fullmatch(value) else None


def bump_suggestions(version: str) -> dict[str, str]:
    match = SEMVER_RE.fullmatch(version)
    if not match:
        return {}
    major, minor, patch = (int(match.group(index)) for index in (1, 2, 3))
    return {
        "patch": f"{major}.{minor}.{patch + 1}",
        "minor": f"{major}.{minor + 1}.0",
        "major": f"{major + 1}.0.0",
        "prerelease_example": f"{major}.{minor}.{patch + 1}-rc.1",
    }


def unique_versions(candidates: Iterable[Candidate]) -> list[str]:
    return sorted({candidate.version for candidate in candidates})


def main() -> int:
    parser = argparse.ArgumentParser(description="Detect project version sources without modifying files")
    parser.add_argument("project", help="Project directory")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()

    root = Path(args.project).expanduser().resolve()
    if not root.is_dir():
        parser.error(f"project directory does not exist: {root}")

    candidates = detect_declared(root)
    declared = unique_versions(candidates)
    tags = git_tags(root)
    semantic_tags = [(tag, semantic_tag(tag)) for tag in tags]
    semantic_tags = [(tag, version) for tag, version in semantic_tags if version]
    latest_tag = semantic_tags[0][0] if semantic_tags else None
    latest_tag_version = semantic_tags[0][1] if semantic_tags else None

    if len(declared) > 1:
        status = "CONFLICT"
        current = None
        reason = "declared version sources disagree"
    elif len(declared) == 1:
        status = "DETECTED"
        current = declared[0]
        reason = "one declared version detected"
    elif latest_tag_version:
        status = "NEEDS_INPUT"
        current = latest_tag_version
        reason = "no declared version; latest semantic tag is only a release-history signal"
    else:
        status = "NEEDS_INPUT"
        current = None
        reason = "no declared version or semantic Git tag detected"

    warnings: list[str] = []
    if current and not SEMVER_RE.fullmatch(current):
        warnings.append("detected version is not Semantic Versioning 2.0.0")
    if len(declared) == 1 and latest_tag_version and declared[0] != latest_tag_version:
        warnings.append(f"declared version {declared[0]} differs from latest tag {latest_tag}")

    payload = {
        "status": status,
        "project": str(root),
        "current_version": current,
        "reason": reason,
        "declared_sources": [asdict(candidate) for candidate in candidates],
        "latest_semantic_tag": latest_tag,
        "latest_tag_version": latest_tag_version,
        "suggestions": bump_suggestions(current) if current else {},
        "warnings": warnings,
        "requires_user_confirmation": True,
    }

    if args.as_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"{status}: {root}")
        print(f"Current version: {current or 'unknown'}")
        for candidate in candidates:
            print(f"- {candidate.source}: {candidate.version}")
        print(f"Latest semantic tag: {latest_tag or 'none'}")
        for warning in warnings:
            print(f"WARNING: {warning}")
        print("User confirmation is required before changing a version, tag, or release.")

    return 2 if status == "CONFLICT" else 1 if status == "NEEDS_INPUT" else 0


if __name__ == "__main__":
    raise SystemExit(main())
