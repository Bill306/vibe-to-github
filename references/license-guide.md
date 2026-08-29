# License decision guide

Use this guide to frame a choice, not to provide legal advice.

## Ask before adding a license

Confirm:

1. Is the repository intended to be open source or only publicly viewable?
2. May others use it commercially?
3. Must distributed modifications remain open source?
4. Should network-hosted modifications trigger reciprocal source sharing?
5. Does an explicit patent grant matter?
6. Who owns the copyright?
7. Does the project contain third-party code, media, fonts, models, or data with separate terms?

## Common choices

| Choice | Typical intent | Important consequence |
|---|---|---|
| MIT | Simple permissive reuse | Requires preservation of copyright and license notice |
| Apache-2.0 | Permissive reuse with explicit patent terms | Includes patent grant and NOTICE-related obligations when applicable |
| GPL-3.0 | Reciprocal distributed software | Distributed derivative software must follow GPL source and license obligations |
| AGPL-3.0 | Reciprocal software including network use | Adds a network-use source-availability condition |
| CC0 / CC-BY / CC-BY-SA | Standalone content or data | Do not use as the default license for software code |
| No license | All rights reserved by default | Public viewing or forking on GitHub does not make the project open source |

Prefer a standard unmodified license text in a root `LICENSE` file so GitHub can detect it. State the SPDX identifier in the README when applicable.

## Boundaries

- Never replace or relicense third-party material under the project's chosen license.
- Never assume the author owns employer, client, course, or commissioned work.
- Separate code and content licenses when they differ.
- Preserve upstream notices and attribution.
- Ask a qualified professional when ownership, patent, commercial, or compatibility risk is material.

Useful primary references:

- [GitHub: Licensing a repository](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository)
- [Choose a License](https://choosealicense.com/)
- [SPDX license list](https://spdx.org/licenses/)
