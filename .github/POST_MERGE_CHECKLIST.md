# Post-Merge Checklist for Repository Admins

After this PR is merged, follow these steps to complete the branch protection setup:

## ✅ Step-by-Step Setup

### 1. Verify Workflows Are Running
- [ ] Go to the **Actions** tab in GitHub
- [ ] Confirm that "CI" and "Lint" workflows are present
- [ ] Check that they run successfully on the `main` branch

### 2. Configure Branch Protection Rules
- [ ] Go to **Settings** → **Branches**
- [ ] Click **Add branch protection rule**
- [ ] Set **Branch name pattern** to `main`
- [ ] Enable: **Require a pull request before merging**
  - [ ] Set required approvals to `1`
  - [ ] Enable: **Dismiss stale pull request approvals when new commits are pushed**
  - [ ] Enable: **Require review from Code Owners**
- [ ] Enable: **Require status checks to pass before merging**
  - [ ] Enable: **Require branches to be up to date before merging**
  - [ ] Add required status checks:
    - [ ] `Run Tests`
    - [ ] `Code Quality Check`
    
    *Note: If these don't appear, wait for the workflows to run once, then come back to add them.*
- [ ] Enable: **Require conversation resolution before merging**
- [ ] Enable: **Do not allow bypassing the above settings** (optional but recommended)
- [ ] Scroll to bottom and disable: **Allow force pushes** (should be unchecked)
- [ ] Scroll to bottom and disable: **Allow deletions** (should be unchecked)
- [ ] Click **Create** to save the rule

### 3. Test the Protection
- [ ] Try to push directly to `main` (should be blocked)
- [ ] Create a test branch and PR
- [ ] Verify that status checks are required
- [ ] Verify that review is required

### 4. Document and Communicate
- [ ] Add a note to your team about the new branch protection rules
- [ ] Share the [CONTRIBUTING.md](../CONTRIBUTING.md) guide with contributors
- [ ] Update any team documentation that references the old workflow

## 📚 Reference Documentation

- **Full Setup Guide**: [BRANCH_PROTECTION.md](BRANCH_PROTECTION.md)
- **Contributing Guide**: [CONTRIBUTING.md](../CONTRIBUTING.md)
- **GitHub Docs**: [About protected branches](https://docs.github.com/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)

## 🎯 What This Accomplishes

Once complete, the `main` branch will be protected from:
- Direct pushes (all changes must go through PRs)
- Force pushes (history cannot be rewritten)
- Deletion (branch cannot be accidentally removed)
- Unreviewed changes (at least 1 approval required)
- Broken code (tests must pass)
- Code quality issues (linting must pass)

## ❓ Need Help?

If you encounter issues:
1. Check the [troubleshooting section](BRANCH_PROTECTION.md#troubleshooting) in BRANCH_PROTECTION.md
2. Review the GitHub documentation linked above
3. Create an issue in this repository

---

**Estimated time to complete**: 5-10 minutes
