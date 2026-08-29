# Security and privacy checklist

Run this checklist before staging and again before pushing. Report filenames and finding classes without printing secret values.

## Credentials and authentication

- Passwords, API keys, tokens, private keys, signing keys, and certificates with private material
- `.env` variants other than deliberately sanitized examples
- Cloud service accounts, OAuth client secrets, cookies, sessions, and browser profiles
- Database connection strings containing credentials
- Credentials embedded in remotes, scripts, notebooks, logs, fixtures, screenshots, or generated files

If a real credential may have been exposed, rotate or revoke it. Removing visible text alone is insufficient.

## Personal and confidential data

- Names, private email addresses, phone numbers, addresses, IDs, financial or health data
- User exports, production databases, chat logs, analytics dumps, customer lists, and private test fixtures
- Employer, client, school, or commissioned materials that the author may not own
- Screenshots containing accounts, notifications, private URLs, or tokens

## Local-machine leakage

- `/Users/...`, `/home/...`, Windows user paths, mounted-drive paths, and internal hostnames
- Temporary directories, logs, caches, IDE state, OS metadata, crash dumps, and local databases
- Absolute links that will break for other users

## Repository hygiene

- `node_modules`, virtual environments, build outputs, coverage, caches, generated binaries, and package artifacts
- Files over 50 MiB require review; GitHub blocks regular Git files over 100 MiB
- Lockfiles should normally be included for applications and handled according to ecosystem norms for libraries
- `.gitignore` must match the actual stack; do not use it to hide a credential that remains in Git history

## Git scope and history

- Inspect untracked, modified, staged, and committed files
- Inspect remotes for embedded credentials
- Check historical filenames for removed `.env`, private-key, credential, database, or personal-data files
- Use a history-aware scanner such as gitleaks when available, with redacted output
- Treat incomplete history scanning as a declared limitation, not a pass

GitHub secret scanning is an additional layer, not a replacement for local review. Supported patterns and push-protection coverage have limits.

## Third-party and supply-chain review

- Verify source and license for copied code, images, fonts, icons, datasets, prompts, and model weights
- Check dependency manifests and lockfiles for accidental local paths or private registries
- Do not publish package-manager credentials or CI secrets
- Distinguish dependency vulnerability review from secret scanning; both may be relevant

## Gate meanings

- `PASS`: no detected blocker in the stated scope.
- `WARNING`: ambiguity, incomplete scan coverage, local path, large file, artifact, or privacy item needs acknowledgement.
- `BLOCKED`: likely live secret, private key, unapproved personal/user data, prohibited file size, or unresolved ownership problem.

The gate is intentionally conservative. A false positive can be reviewed; a leaked credential cannot be recalled.
