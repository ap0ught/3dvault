# Branch Protection Setup Guide

This guide provides step-by-step instructions for repository administrators to enable branch protection on the `main` branch.

## Overview

Branch protection rules help maintain code quality and prevent accidental changes to important branches. This repository includes automated CI/CD workflows that provide status checks for branch protection.

## Prerequisites

- Repository admin access
- The CI/CD workflows in `.github/workflows/` are committed to the repository

## Automated Status Checks Available

Once this PR is merged, the following status checks will be available:

1. **Run Tests** (from `ci.yml` workflow)
   - Runs the full test suite
   - Verifies all tests pass before allowing merge

2. **Code Quality Check** (from `lint.yml` workflow)
   - Checks for Python syntax errors
   - Validates code quality standards

## Setting Up Branch Protection

### Step 1: Access Branch Protection Settings

1. Go to your repository on GitHub
2. Click on **Settings** (top menu)
3. In the left sidebar, click **Branches** (under "Code and automation")
4. Click **Add branch protection rule** (or **Add rule** if no rules exist)

### Step 2: Configure Basic Protection

In the **Branch name pattern** field, enter: `main`

Enable the following settings:

#### Require Pull Request Reviews
- ✅ **Require a pull request before merging**
  - Set **Required number of approvals before merging** to: `1`
  - ✅ **Dismiss stale pull request approvals when new commits are pushed**
  - ✅ **Require review from Code Owners** (uses the `CODEOWNERS` file)

#### Require Status Checks
- ✅ **Require status checks to pass before merging**
  - ✅ **Require branches to be up to date before merging**
  - In the search box, find and add these required checks:
    - `Run Tests`
    - `Code Quality Check`
  
  *Note: These checks will only appear after the workflows have run at least once. You may need to merge this PR first, then edit the rule to add the required checks.*

#### Additional Settings
- ✅ **Require conversation resolution before merging**
- ✅ **Require linear history** (optional, enforces clean commit history)
- ✅ **Do not allow bypassing the above settings**

### Step 3: Prevent Force Pushes and Deletion

Scroll down to the bottom of the rule configuration:

- ✅ **Do not allow force pushes**
  - Prevents force pushing to `main` (protects against rewriting history)
  
- ✅ **Allow deletions**
  - Leave this **UNCHECKED** to prevent deletion of the `main` branch

### Step 4: Save the Rule

Click **Create** (or **Save changes** if editing an existing rule)

## Verifying Protection is Active

After saving, you should see:

1. A shield icon next to the `main` branch in the branch dropdown
2. Attempts to push directly to `main` will be blocked
3. Pull requests to `main` will show required checks

### Test the Protection

Try to push directly to `main`:
```bash
git checkout main
git commit --allow-empty -m "Test commit"
git push origin main
```

You should see an error message like:
```
remote: error: GH006: Protected branch update failed for refs/heads/main.
```

This confirms the protection is working!

## GitHub Rulesets (Alternative Method)

GitHub also supports a newer "Rulesets" feature that can provide similar protection. To use rulesets instead:

1. Go to **Settings** → **Rules** → **Rulesets**
2. Click **New ruleset** → **New branch ruleset**
3. Configure similar rules as above
4. Target the `main` branch

Rulesets provide more flexibility and can be defined in code (for GitHub Enterprise), but branch protection rules are more common and work across all GitHub plans.

## Troubleshooting

### Required checks don't appear in the list

**Problem**: You can't find "Run Tests" or "Code Quality Check" in the status checks list.

**Solution**: 
1. The workflows need to run at least once before they appear as available status checks
2. Make sure this PR is merged to `main`
3. Verify the workflows are running by checking the **Actions** tab
4. After workflows complete, edit the branch protection rule and the checks should be available

### Workflow fails on first run

**Problem**: CI or Lint workflow fails.

**Solution**:
1. Check the workflow logs in the **Actions** tab
2. Common issues:
   - Missing dependencies (should be in `requirements.txt`)
   - Database migration issues (the workflow runs migrations)
   - Test failures (fix the failing tests)

### Can't bypass protection even as admin

**Problem**: Admin can't push emergency fixes.

**Solution**:
1. Option 1: Temporarily disable "Do not allow bypassing" in branch protection settings
2. Option 2: Use the "Bypass list" feature in branch protection to allow specific users
3. Option 3: Create a hotfix PR and have it fast-tracked through review

## Additional Resources

- [GitHub Branch Protection Documentation](https://docs.github.com/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)
- [GitHub Rulesets Documentation](https://docs.github.com/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets)
- [GitHub Actions Status Checks](https://docs.github.com/pull-requests/collaborating-with-pull-requests/collaborating-on-repositories-with-code-quality-features/about-status-checks)

## Summary

Once configured, your `main` branch will be protected with:
- ✅ Required pull request reviews
- ✅ Required status checks (tests + linting)
- ✅ Conversation resolution required
- ✅ No force pushes allowed
- ✅ No branch deletion allowed

This ensures code quality and prevents accidental changes to the production branch! 🛡️
