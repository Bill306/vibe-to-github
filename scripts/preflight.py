#!/usr/bin/env python3
"""Read-only GitHub publication preflight.

The scanner reports filenames and finding types but never prints matched secret values.
It is intentionally heuristic and does not claim to prove that a project is safe.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
from dataclasses import asdict, dataclass
from typing import Iterable


TEXT_EXTENSIONS = {
    ".c", ".cc", ".conf", ".cpp", ".css", ".csv", ".env", ".go", ".h",
    ".html", ".ini", ".java", ".js", ".json", ".jsx", ".kt", ".md",
    ".mjs", ".properties", ".py", ".rb", ".rs", ".scss", ".sh", ".sql",
    ".svg", ".toml", ".ts", ".tsx", ".txt", ".xml", ".yaml", ".yml",
}

SKIP_DIRS = {
    ".git", ".hg", ".svn", "node_modules", "vendor", ".venv", "venv",
    "__pycache__", ".pytest_cache", ".mypy_cache", ".next", ".nuxt", "dist",
    "build", "coverage", ".cache", ".turbo",
}

ARTIFACT_DIRS = {
    "node_modules", ".venv", "venv", "__pycache__", ".pytest_cache", ".next",
    ".nuxt", "dist", "build", "coverage", ".cache", ".turbo", "tmp", ".tmp",
}

BLOCKED_FILENAMES = {
    ".env", ".env.local", ".env.production", ".env.development.local",
    "credentials.json", "service-account.json", "cookies.txt", "id_rsa", "id_dsa",
}

BLOCKED_SUFFIXES = {".key", ".p12", ".pfx", ".sqlite", ".sqlite3", ".db"}
WARNING_SUFFIXES = {".log", ".swp", ".tmp", ".bak", ".dmp"}

PLACEHOLDER_WORDS = re.compile(
    r"(?i)(example|sample|placeholder|changeme|replace[-_ ]?me|your[-_ ]|dummy|fake|"
    r"test[-_ ]?(key|token|secret)|xxx+|<[^>]+>|\$\{[^}]+\})"
)

SECRET_PATTERNS = [
    ("private key material", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----")),
    ("GitHub token", re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{20,}\b")),
    ("OpenAI-style key", re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b")),
    ("AWS access key", re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b")),
    ("credential assignment", re.compile(
        r"(?i)\b(?:api[_-]?key|secret|token|password|passwd|client[_-]?secret)\b\s*[:=]\s*"
        r"[\"']?([^\s\"'`,;]{8,})"
    )),
    ("credential-bearing URL", re.compile(r"(?i)\b(?:postgres|mysql|mongodb(?:\+srv)?|redis)://[^\s/@:]+:[^\s/@]+@")),
]

ABSOLUTE_PATH_PATTERNS = [
    re.compile(r"/Users/[A-Za-z0-9][A-Za-z0-9._-]*/"),
    re.compile(r"/home/[A-Za-z0-9][A-Za-z0-9._-]*/"),
    re.compile(r"[A-Za-z]:\\Users\\[A-Za-z0-9][^\\\s]*\\"),
]

EMAIL_PATTERN = re.compile(r"(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b")


@dataclass(frozen=True)
class Finding:
    severity: str
    category: str
    path: str
    detail: str


def run_git(root: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(root), *args],
        check=False,
        capture_output=True,
        text=True,
        timeout=45,
    )


def git_root(root: Path) -> Path | None:
    result = run_git(root, ["rev-parse", "--show-toplevel"])
    if result.returncode != 0:
        return None
    try:
        return Path(result.stdout.strip()).resolve()
    except OSError:
        return None


def read_ignore_patterns(root: Path) -> list[str]:
    path = root / ".gitignore"
    if not path.is_file():
        return []
    patterns: list[str] = []
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if line and not line.startswith("#") and not line.startswith("!"):
            patterns.append(line.rstrip("/"))
    return patterns


def is_ignored(relative: str, patterns: Iterable[str]) -> bool:
    parts = Path(relative).parts
    for pattern in patterns:
        normalized = pattern.lstrip("/")
        if fnmatch.fnmatch(relative, normalized) or fnmatch.fnmatch(Path(relative).name, normalized):
            return True
        if normalized in parts:
            return True
    return False


def likely_text(path: Path) -> bool:
    if path.suffix.lower() in TEXT_EXTENSIONS or path.name.startswith(".env"):
        return True
    try:
        sample = path.read_bytes()[:4096]
    except OSError:
        return False
    return b"\x00" not in sample


def scan_text(path: Path, relative: str) -> list[Finding]:
    findings: list[Finding] = []
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return [Finding("WARNING", "unreadable file", relative, str(exc))]

    for label, pattern in SECRET_PATTERNS:
        for match in pattern.finditer(text):
            candidate = match.group(1) if match.lastindex else match.group(0)
            if label == "credential assignment" and PLACEHOLDER_WORDS.search(candidate):
                continue
            line = text.count("\n", 0, match.start()) + 1
            findings.append(Finding("BLOCKED", "possible secret", relative, f"{label} near line {line}"))
            break

    for pattern in ABSOLUTE_PATH_PATTERNS:
        match = pattern.search(text)
        if match:
            line = text.count("\n", 0, match.start()) + 1
            findings.append(Finding("WARNING", "local absolute path", relative, f"machine-specific path near line {line}"))
            break

    if path.suffix.lower() in {".csv", ".json", ".sql", ".log", ".txt"}:
        match = EMAIL_PATTERN.search(text)
        if match:
            line = text.count("\n", 0, match.start()) + 1
            findings.append(Finding("WARNING", "possible personal data", relative, f"email-like value near line {line}"))

    return findings


def scan_tree(root: Path, ignore_patterns: list[str]) -> list[Finding]:
    findings: list[Finding] = []

    for child in root.iterdir():
        if child.is_dir() and child.name in ARTIFACT_DIRS and not is_ignored(child.name, ignore_patterns):
            findings.append(Finding("WARNING", "generated or local directory", child.name, "directory exists and is not clearly ignored"))

    for current, dirs, files in os.walk(root):
        current_path = Path(current)
        relative_dir = current_path.relative_to(root)
        dirs[:] = [
            name for name in dirs
            if name not in SKIP_DIRS and not is_ignored(str(relative_dir / name), ignore_patterns)
        ]
        for name in files:
            path = current_path / name
            relative = path.relative_to(root).as_posix()
            lower_name = name.lower()
            suffix = path.suffix.lower()
            ignored = is_ignored(relative, ignore_patterns)
            sensitive_name = lower_name in BLOCKED_FILENAMES or (
                lower_name.startswith(".env.") and not lower_name.endswith((".example", ".sample", ".template"))
            )
            if sensitive_name:
                severity = "WARNING" if ignored else "BLOCKED"
                detail = "sensitive local file exists but appears ignored; never stage it" if ignored else "credential or environment file requires review"
                findings.append(Finding(severity, "sensitive filename", relative, detail))
            if suffix in BLOCKED_SUFFIXES:
                severity = "WARNING" if ignored else "BLOCKED"
                detail = "sensitive local data file appears ignored; verify it has never been committed" if ignored else f"{suffix or 'data'} file requires explicit review"
                findings.append(Finding(severity, "sensitive data file", relative, detail))
            elif suffix in WARNING_SUFFIXES or lower_name in {".ds_store", "thumbs.db"}:
                findings.append(Finding("WARNING", "temporary or local file", relative, "exclude from publication unless deliberately needed"))

            if ignored:
                continue

            try:
                size = path.stat().st_size
            except OSError:
                continue
            if size > 100 * 1024 * 1024:
                findings.append(Finding("BLOCKED", "file size", relative, "file exceeds GitHub's 100 MiB regular Git limit"))
            elif size > 50 * 1024 * 1024:
                findings.append(Finding("WARNING", "file size", relative, "file exceeds 50 MiB and will trigger a GitHub warning"))

            if size <= 5 * 1024 * 1024 and likely_text(path):
                findings.extend(scan_text(path, relative))

    return findings


def scan_git_metadata(root: Path, repository: Path | None, history: bool) -> tuple[list[Finding], str]:
    findings: list[Finding] = []
    if repository is None:
        findings.append(Finding("WARNING", "Git coverage", ".", "not a Git repository; staged and history checks were not available"))
        return findings, "unavailable"

    if repository != root:
        findings.append(Finding("WARNING", "repository boundary", ".", f"project is inside parent repository {repository}"))

    remotes = run_git(root, ["remote", "-v"])
    if remotes.returncode == 0 and re.search(r"(?i)https?://[^/@\s:]+:[^/@\s]+@", remotes.stdout):
        findings.append(Finding("BLOCKED", "remote credential", ".git/config", "a remote URL appears to contain embedded credentials"))

    if not history:
        findings.append(Finding("WARNING", "history coverage", ".git", "history scan not requested; rerun with --history before publication"))
        return findings, "not requested"

    names = run_git(root, ["log", "--all", "--name-only", "--pretty=format:"])
    if names.returncode == 0:
        risky: set[str] = set()
        for raw in names.stdout.splitlines():
            value = raw.strip()
            if not value:
                continue
            base = Path(value).name.lower()
            suffix = Path(value).suffix.lower()
            if base in BLOCKED_FILENAMES or suffix in BLOCKED_SUFFIXES or (base.startswith(".env.") and not base.endswith((".example", ".sample", ".template"))):
                risky.add(value)
        for value in sorted(risky):
            findings.append(Finding("BLOCKED", "historical sensitive filename", value, "sensitive-looking file exists in Git history"))
    else:
        findings.append(Finding("WARNING", "history coverage", ".git", "could not enumerate historical filenames"))

    gitleaks = shutil.which("gitleaks")
    if not gitleaks:
        findings.append(Finding("WARNING", "history coverage", ".git", "gitleaks is unavailable; content-level history scan was not performed"))
        return findings, "filenames only"

    with tempfile.TemporaryDirectory(prefix="vibe-to-github-") as temp_dir:
        report = Path(temp_dir) / "gitleaks.json"
        result = subprocess.run(
            [gitleaks, "git", "--redact", "--report-format", "json", "--report-path", str(report), str(repository)],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=180,
        )
        if result.returncode == 1 and report.is_file():
            try:
                leaks = json.loads(report.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                leaks = []
            paths = sorted({str(item.get("File", ".git")) for item in leaks if isinstance(item, dict)})
            detail = f"gitleaks reported {len(leaks)} redacted finding(s)"
            for value in paths[:20] or [".git"]:
                findings.append(Finding("BLOCKED", "history secret scan", value, detail))
        elif result.returncode not in {0, 1}:
            findings.append(Finding("WARNING", "history coverage", ".git", "gitleaks could not complete; content-level history scan is incomplete"))
            return findings, "filenames only"

    return findings, "gitleaks plus filenames"


def dedupe(findings: Iterable[Finding]) -> list[Finding]:
    return sorted(set(findings), key=lambda item: ({"BLOCKED": 0, "WARNING": 1}.get(item.severity, 2), item.path, item.category))


def main() -> int:
    parser = argparse.ArgumentParser(description="Read-only GitHub publication preflight")
    parser.add_argument("project", help="Project directory to inspect")
    parser.add_argument("--history", action="store_true", help="Inspect Git history filenames and use gitleaks when available")
    parser.add_argument("--json", action="store_true", dest="as_json", help="Emit JSON")
    args = parser.parse_args()

    root = Path(args.project).expanduser().resolve()
    if not root.is_dir():
        parser.error(f"project directory does not exist: {root}")

    ignore_patterns = read_ignore_patterns(root)
    findings = scan_tree(root, ignore_patterns)
    git_findings, history_coverage = scan_git_metadata(root, git_root(root), args.history)
    findings = dedupe([*findings, *git_findings])

    severity = "BLOCKED" if any(item.severity == "BLOCKED" for item in findings) else "WARNING" if findings else "PASS"
    payload = {
        "status": severity,
        "project": str(root),
        "history_coverage": history_coverage,
        "findings": [asdict(item) for item in findings],
        "disclaimer": "Heuristic read-only scan; PASS is not proof that a repository is safe.",
    }

    if args.as_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"{severity}: {root}")
        print(f"History coverage: {history_coverage}")
        for item in findings:
            print(f"[{item.severity}] {item.category}: {item.path} — {item.detail}")
        print(payload["disclaimer"])

    return 2 if severity == "BLOCKED" else 1 if severity == "WARNING" else 0


if __name__ == "__main__":
    raise SystemExit(main())
