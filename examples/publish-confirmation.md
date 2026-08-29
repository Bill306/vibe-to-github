# Example: publication confirmation gate

Before creating or updating a GitHub repository, present a manifest like this:

```text
Project: /projects/meal-planner
GitHub target: example-owner/meal-planner
Action: create new repository
Visibility: private
Default branch: main
Files: README.md, LICENSE, .gitignore, .env.example, existing source files
README: PASS
License: MIT, copyright holder confirmed by user
Security: PASS
History coverage: gitleaks plus historical filename scan
Verification: lint, typecheck, test, and build passed
Deployment: not requested
Proposed remote action: create private repository and push main without force
```

Ask the user to confirm the manifest. Do not interpret approval of local README edits as approval of the remote action.
