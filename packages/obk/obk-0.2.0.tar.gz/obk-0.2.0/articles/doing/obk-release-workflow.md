# OBK Release Workflow

## Overview

The OBK Release Workflow governs all official deployments to PyPI from the `main` branch.  
It ensures every release is deliberate, tested, and documented, and provides full control over when and how deployment happens—using protected PRs, explicit commit-message triggers, and post-release maintenance steps for accuracy.

## Step-by-Step Release Workflow

1. **Prepare and Merge Features to Main**
    
    * Finish all feature development and merge PRs to `main` as described in OBK Feature Workflow.
        
    * Confirm all tests and status checks pass before proceeding.
        
2. **Open a Deployment PR to Main**
    
    * From your release-ready branch (`feature/*` or `release/*`).
        
    * Use the PR checklist:
        
        * Check “This PR is a deployment PR (intended to publish to PyPI)”.
            
        * Prepare to include `[deploy]` in the squash-merge commit message.
            
3. **Update the README.md**
    
    * Before final review, update `README.md` to document any new features, changes, or usage instructions.
        
    * Reference the recurring task in `tasks/recurring/task-readme.md` if automation or template guidance is needed.
        
4. **Review and Approve**
    
    * Reviewers confirm:
        
        * Tests pass
            
        * `README.md` is updated
            
        * Version in `pyproject.toml` is correct (pre-release)
            
    * Only reviewers/maintainers may approve protected `main` merges.
        
5. **Squash-Merge to Main (with `[deploy]`)**
    
    * **Include `[deploy]` in the squash-merge commit message** (e.g., `feat: new feature [deploy]`).
        
    * Omit `[deploy]` for non-release PRs (CI will test/build but skip deploy).
        
6. **CI/CD Pipeline Executes**
    
    * **Test:** Run all tests (`pytest`, lint, etc.).
        
    * **Build:** Build the distribution package.
        
    * **Deploy:**
        
        * **Only runs if `[deploy]` is in the commit message**
            
        * Bumps the patch version in `pyproject.toml` (local to runner)
            
        * Uploads to PyPI via Twine using repository secrets.
            
    * Any test or build failure halts deploy.
        
7. **Verify PyPI Publication**
    
    * Confirm the new version is available on [PyPI](https://pypi.org/).
        
    * Optionally, install and test from PyPI to verify.
        
8. **Post Release: Sync Version in pyproject.toml (Manual)**
    
    * The deploy script bumps the version but does **not** commit it.
        
    * **Manually create a branch:**  
        `ci/update-version-YYYYMMDD`
        
    * Update `pyproject.toml` to match the deployed version.
        
    * Commit, push, open PR, and merge to `main`.
        
9. **Post Release: Publish GitHub Release**
    
    * Use [Release Drafter](.github/workflows/release-drafter.yml) or do it manually.
        
    * Clean up automated notes and release contents as needed.
        
10. **Update Changelog and Docs (Manual or via Codex)**
    
    * After the GitHub Release, update `CHANGELOG.md` and any relevant docs.
        
    * Use Codex automation or manual edits as needed. There is a recurring task for this.
        
    * Always merge these as **non-deployment PRs** (no `[deploy]`).
        


## Key Policies and Notes

* **Deploys Only from Main:**  
    The `main` branch is the only deploy branch—no other branch may publish to PyPI.
    
* **Commit-Message-Driven Deploy:**  
    The `[deploy]` tag in a squash-merge commit message is **required** for PyPI publish; all other merges are non-deployment.
    
* **Branch Protection Enforced:**  
    All merges to `main` must be via PR, with required status checks and reviews.
    
* **Automated Patch Version Bump:**  
    Each deploy bumps the patch version, ensuring unique PyPI uploads.  
    Manual version sync is required after each deploy.
    
* **Post-Release Maintenance Required:**  
    After every release, you must:
    
    * Manually sync the new version to `pyproject.toml`
        
    * Update changelog and documentation to match the GitHub release.
        
* **Codex Automation for Docs:**  
    Use Codex only after releases, and always as non-deployment PRs.
    

* * *

## References

* [main-branch-pypi-cd-scaffold.md](main-branch-pypi-cd-scaffold.md)
    
* OBK Feature Workflow
    
* [PR Template](.github/pull_request_template.md)
    
* [CI/CD Pipeline](.github/workflows/ci-cd.yml)
    
* [Release Drafter](.github/workflows/release-drafter.yml)
    
* [bump_patch.py Script](.github/scripts/bump_patch.py)
    
* [PyPI Token Setup](https://pypi.org/help/#apitoken)
    

* * *

## Summary

**Every OBK release is:**

* Fully reviewed and tested before merging to `main`
    
* Explicitly triggered via `[deploy]` in the commit message
    
* Version-bumped and published only if tests/build pass
    
* Synchronized post-release to keep repo version and documentation accurate
    

_This process is frozen until future team consensus and documentation update._

* * *