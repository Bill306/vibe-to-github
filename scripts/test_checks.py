#!/usr/bin/env python3
"""Smoke tests for the deterministic README and safety checks."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile


SCRIPT_DIR = Path(__file__).resolve().parent


SAFE_README = """# Fixture App

A small verified fixture used to test repository documentation checks.

## Problem

Developers need a deterministic fixture for README validation.

## Features

- **Echo** — Returns the supplied value.

## Installation

```bash
npm install
```

## Usage

Live demo: verified only inside this test fixture.

```bash
npm run build
```

## Input and Output Example

Input: `hello`

Output: `hello`

## Known Limitations

- This is a test fixture, not a deployed application.

## Security

The fixture stores no user data.

## License

MIT License. See [LICENSE](LICENSE).
"""


def run_json(script: str, *args: str) -> tuple[int, dict]:
    result = subprocess.run(
        [sys.executable, str(SCRIPT_DIR / script), *args, "--json"],
        check=False,
        capture_output=True,
        text=True,
    )
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise AssertionError(f"{script} did not return JSON: {result.stdout}\n{result.stderr}") from exc
    return result.returncode, payload


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="vibe-to-github-tests-") as temp:
        base = Path(temp)
        safe = base / "safe"
        unsafe = base / "unsafe"
        safe.mkdir()
        unsafe.mkdir()

        (safe / "README.md").write_text(SAFE_README, encoding="utf-8")
        (safe / "LICENSE").write_text("MIT License\n", encoding="utf-8")
        (safe / "package.json").write_text(
            json.dumps({"scripts": {"build": "node -e \"process.exit(0)\""}, "dependencies": {"next": "1.0.0"}}),
            encoding="utf-8",
        )
        (safe / ".gitignore").write_text("node_modules/\n.env*\n!.env.example\n", encoding="utf-8")

        code, payload = run_json("validate_readme.py", str(safe))
        assert code == 0, payload
        assert payload["status"] == "PASS", payload

        (unsafe / "README.md").write_text("# Broken\n\nTODO: document this.\n", encoding="utf-8")
        secret_value = "live_" + "fixturecredentialvalue1234567890"
        credential_name = "API_" + "KEY"
        (unsafe / ".env.local").write_text(f"{credential_name}={secret_value}\n", encoding="utf-8")
        (unsafe / "users.sqlite").write_bytes(b"not a real database")

        code, payload = run_json("validate_readme.py", str(unsafe))
        assert code == 2, payload
        assert payload["status"] == "BLOCKED", payload

        code, payload = run_json("preflight.py", str(unsafe))
        assert code == 2, payload
        assert payload["status"] == "BLOCKED", payload
        serialized = json.dumps(payload)
        assert secret_value not in serialized, "secret value leaked in scanner output"
        categories = {item["category"] for item in payload["findings"]}
        assert "sensitive filename" in categories, payload
        assert "sensitive data file" in categories, payload

    print("vibe-to-github checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
