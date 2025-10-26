# Branch Protection Setup

## Overview

This document provides instructions for protecting the `main` branch of this repository to prevent accidental force pushes, deletions, and ensure code quality through required reviews and status checks.

## Why Branch Protection?

Branch protection rules help maintain code quality and stability by:
- Preventing force pushes that could rewrite history
- Preventing accidental branch deletion
- Requiring pull request reviews before merging
- Ensuring CI/CD checks pass before merging
- Maintaining a clean commit history

## Setup Instructions

### Option 1: Using the GitHub UI (Recommended)

1. Navigate to your repository on GitHub
2. Go to **Settings** → **Code and automation** → **Rules** → **Rulesets**
3. Click **New ruleset** → **New branch ruleset**
4. Configure the ruleset:
   - **Name**: "Main Branch Protection"
   - **Enforcement status**: Active
   - **Target branches**: Add `main` as an included branch
5. Select the following rules (recommended):
   - ✅ **Restrict deletions** - Prevents branch deletion
   - ✅ **Require a pull request before merging** - Enforces code review
     - Require approvals: 1 (adjust as needed)
     - Dismiss stale pull request approvals when new commits are pushed (optional)
   - ✅ **Require status checks to pass** - Ensures tests/builds pass (if applicable)
   - ✅ **Block force pushes** - Prevents rewriting history
6. Click **Create**

### Option 2: Import Preconfigured Ruleset

A ready-to-use ruleset configuration is available in this repository at `.github/ruleset-main-branch-protection.json`.

To import it:

1. Navigate to your repository on GitHub
2. Go to **Settings** → **Code and automation** → **Rules** → **Rulesets**
3. Click **New ruleset** → **Import a ruleset**
4. Upload the file `.github/ruleset-main-branch-protection.json`
5. Review the settings and click **Create**

### Option 3: Using the GitHub API

If you prefer to use the API or automate the setup, you can use the GitHub REST API:

```bash
# Example using curl (requires a GitHub token with admin permissions)
curl -X POST \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  https://api.github.com/repos/OWNER/REPO/rulesets \
  -d @.github/ruleset-main-branch-protection.json
```

Replace `OWNER` with your GitHub username or organization and `REPO` with your repository name.

## Recommended Settings

For this repository, we recommend the following minimum protections:

| Rule | Setting | Reason |
|------|---------|--------|
| **Restrict deletions** | Enabled | Prevents accidental deletion of main branch |
| **Block force pushes** | Enabled | Maintains clean git history |
| **Require pull requests** | 1 approval | Ensures code review before merging |
| **Require status checks** | Optional | Enable if you have CI/CD workflows |

## Verifying Protection

After setting up branch protection, you can verify it's active by:

1. Going to **Settings** → **Rules** → **Rulesets**
2. Confirming the ruleset status is "Active"
3. Attempting to push directly to `main` (should be blocked)

## Troubleshooting

### "I can't push to main anymore"

This is expected! Branch protection requires you to:
1. Create a feature branch
2. Make your changes
3. Open a pull request
4. Get required approvals
5. Merge via pull request

### "I need to bypass protection for an emergency fix"

If you're a repository administrator:
1. You can temporarily disable the ruleset in Settings
2. Make your emergency change
3. Re-enable the ruleset immediately after

Alternatively, configure bypass permissions in the ruleset settings to allow specific users or teams to bypass rules when needed.

## References

- [GitHub Docs: About rulesets](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets)
- [GitHub Docs: Creating rulesets for a repository](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/creating-rulesets-for-a-repository)
- [GitHub Docs: Available rules for rulesets](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets)
