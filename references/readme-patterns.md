# README patterns

## Purpose

Make the first two screens answer four questions: What is this? Who is it for? What can it do? How do I try it?

The patterns below derive from the information hierarchy used by [React](https://github.com/react/react/blob/main/README.md), [Supabase](https://github.com/supabase/supabase/blob/master/README.md), [freeCodeCamp](https://github.com/freeCodeCamp/freeCodeCamp/blob/main/README.md), [System Design Primer](https://github.com/donnemartin/system-design-primer/blob/master/README.md), [Build Your Own X](https://github.com/codecrafters-io/build-your-own-x), [Awesome](https://github.com/sindresorhus/awesome), and [Public APIs](https://github.com/public-apis/public-apis). Learn their hierarchy and consistency; do not copy their scale, branding, or prose.

## Universal rules

1. Use one H1 for the project name.
2. Follow it with one concrete value sentence, not a slogan alone.
3. Put a real demo, screenshot, or minimum runnable example near the top when it materially helps.
4. Include only verifiable badges that aid decisions: license, release/package, build, tests, or contribution status. Prefer zero to six.
5. Use H2 headings for user tasks and H3 headings for variants.
6. Use ordered lists for sequences, code fences for commands, and tables only for comparisons or repeated fields.
7. Keep list grammar consistent: `Name — one-sentence explanation`.
8. Use meaningful image alt text and repository-relative paths for repository images.
9. Add a visible table of contents only for a genuinely long README. GitHub already provides an Outline from headings.
10. Move deep material to `docs/`, `CONTRIBUTING.md`, or `SECURITY.md`; link from a concise summary.
11. Put sponsor walls, community promotion, and maintainer detail after the user's success path.
12. Do not claim compatibility, performance, security, or test status without evidence.

## App or product

Use `assets/templates/app-product.md`. Prioritize a real demo, one representative screenshot, main user workflows, fastest experience and local-development paths, safe configuration guidance, known limitations, and data handling.

## Library or CLI

Use `assets/templates/library-cli.md`. Prioritize installation, a minimum copyable example, input/output, supported runtime, the main API or flags, and a link to deeper documentation. Do not force a hero image when code communicates the product better.

## Community or content

Use `assets/templates/community-content.md`. Prioritize scope, audience, clickable categories, consistent item format, contribution criteria, and content ownership. Use Creative Commons guidance only after confirming the intended permissions.

## Required content contract

Every README must communicate the problem and intended user, main features that exist today, installation or access method, usage instructions, and at least one realistic input/output example. Also include configuration, limitations, security, contribution, support, and license when relevant.

Do not fill missing facts with generic prose; ask the user or mark the item unknown.

## Formatting anti-patterns

- Badge walls or badges for checks never run
- A long origin story before the first runnable path
- Screenshots of an older or different UI
- Huge manually maintained directories for small projects
- Tables used for procedural steps
- Decorative emoji as the only source of structure
- Mixed HTML layout and repeated `<br>` tags without a concrete rendering need
- Bare links without descriptive text
- Placeholder text such as `TODO`, `your-project`, or fabricated examples
