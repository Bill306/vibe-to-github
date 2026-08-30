# Version confirmation guide

Use this guide to identify the current version and ask for the intended release version. Detection is evidence; it is not authorization to change anything.

## Detect sources

Run:

```bash
python3 scripts/detect_version.py /absolute/path/to/project
```

Inspect, when present:

- `package.json` version
- `pyproject.toml` project or Poetry version
- `Cargo.toml` package version
- `setup.cfg` metadata version
- `VERSION`, `VERSION.txt`, or `.version`
- Latest semantic Git tag, commonly `vX.Y.Z`
- Package registry or GitHub Release version only when the user asks for live verification

Prefer one declared source of truth. If declared files disagree, stop and ask which source is canonical. Do not silently synchronize them.

## Ask the version questions

Always confirm:

1. "I detected the current version as X from SOURCE. Is that correct?"
2. "What version should this publication use?"
3. If the answer is a change type, confirm the exact result before editing: Patch, Minor, Major, or Prerelease.

If no version exists, ask whether this is an experimental first release or a stable public release. `0.1.0` is a reasonable SemVer starting point for initial development; use `1.0.0` only when the user confirms the public interface is stable.

## Apply Semantic Versioning when appropriate

- Patch `X.Y.Z+1`: backward-compatible bug fixes.
- Minor `X.Y+1.0`: backward-compatible functionality.
- Major `X+1.0.0`: incompatible public-interface changes.
- Prerelease: append a label such as `-alpha.1`, `-beta.1`, or `-rc.1`.

Semantic Versioning requires a defined public API. Apps, content collections, data snapshots, or internal tools may use another existing version scheme; preserve it rather than forcing SemVer.

Primary reference: [Semantic Versioning 2.0.0](https://semver.org/).

## Separate authorizations

Confirm each action that applies:

- Edit the canonical version file
- Synchronize secondary version files
- Commit the version change
- Create an annotated or lightweight Git tag
- Push the tag
- Create a GitHub Release
- Publish to a package registry

A request to push source code does not automatically authorize a tag, GitHub Release, registry publication, or deployment.

## Add to the publication manifest

```text
Detected current version: X.Y.Z from SOURCE
Latest release tag: vX.Y.Z or none
Confirmed release version: X.Y.Z
Version change: none | patch | minor | major | prerelease | custom scheme
Authorized actions: edit manifest | commit | tag | push tag | GitHub Release
```
