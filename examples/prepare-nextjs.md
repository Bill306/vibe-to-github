# Example: prepare a Next.js app without publishing

## User request

```text
Use $vibe-to-github to prepare /projects/meal-planner for GitHub. Do not publish it yet.
```

## Expected behavior

1. Resolve the project boundary and inspect manifests, scripts, Git state, remotes, and current README.
2. Run the read-only preflight, including history coverage.
3. Derive real features and commands from the code; ask for any missing product facts.
4. Select the App/Product README pattern and add only evidence-backed content.
5. Recommend license options and wait for the user's choice before writing `LICENSE`.
6. Run available lint, typecheck, tests, build, and README validation.
7. Return a local preparation report and perform no remote action.

## Example result shape

```text
Status: PARTIAL
Project: /projects/meal-planner
README: PASS
Security: WARNING — content-level Git history scan unavailable
Verification:
- npm run typecheck -> exit 0 -> TypeScript check passed in this environment
- npm run build -> exit 0 -> production bundle built in this environment
License: awaiting user confirmation
Remote action: none performed
```
