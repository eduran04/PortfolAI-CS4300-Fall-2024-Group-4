# Example Development Workflow Guide

### 1. Before Making Changes
```bash
# Pull latest changes from main
git checkout main
git pull origin main
```

### 2. Create Feature Branch
```bash
# Create and switch to new branch
git checkout -b feature/your-feature-name

# Example:
git checkout -b feature/add-user-authentication
```

### 3. Make Your Changes
- Add, Delete, Refactor the code.
- Test Changes Locally First Please. 

### 4. Commit and Push
```bash
# Add your changes
git add .

# Commit with descriptive message
git commit -m "Add new chat bot window" # My best shot at being descriptive plz give feeback -ED

# Push to GitHub
git push origin feature/your-feature-name
```

### 5. Create Pull Request
1. Go to GitHub repository
2. Click "Compare & pull request"
3. Fill in:
   - **Title**: Brief description of changes
   - **Description**: What you changed and why
4. Click "Create pull request"

### 6. Wait for AI Code Review
- **AI will automatically review** your code using gpt-4o-mini (or whatever model we use)
- **CI Pipeline** will run tests and checks
- **Coverage** will check test coverage
- **Security** will scan for vulnerabilities

### 7. Address Feedback
- Read the AI review comments
- Make requested changes
- Push updates to the same branch
- AI will review again automatically

### 8. Merge to Main
- Once approved, merge the PR
- Delete the feature branch (GitHub option)
- Switch back to main locally

```bash
git checkout main
git pull origin main
```

### 9. Clean Up Feature Branch
After merging, clean up branches:

Note: Their might be other ways to do this

```bash
# Delete local branch
git branch -d feature/your-feature-name

# Delete remote branch (if not auto-deleted by GitHub)
git push origin --delete feature/your-feature-name

# Verify cleanup
git branch -a
```

---

## GitHub Actions Workflows

### What Runs Automatically:
1. **AI Code Review** - Reviews every PR with AI
2. **CI Pipeline** - Runs tests, migrations, static files
3. **Coverage** - Checks test coverage (must be >80%)
4. **Security** - Scans for security issues

### Manual Triggers:
- Go to **Actions** tab → **Custom Code Review** → **Run workflow**
- Use when you want an extra AI review

---

## Branch Naming Convention

Use descriptive branch names:
- `feature/add-login-system`
- `bugfix/fix-api-error`
- `hotfix/security-patch`
- `refactor/cleanup-views`

---

## Important Rules

### DO:
- Always create feature branches
- Write descriptive commit messages
- Wait for AI review before merging
- Keep test coverage above 80%
- Pull latest main before starting work

### DON'T:
- Push directly to main (plz don't)
- Merge without AI review
- Ignore failing CI checks
- Skip writing commit messages

---

## Current Issues 

- We still need to add the Open AI Key in Github Secrets for the Code review to work.

---

---

## Best Practice Workflow according to Claude Sonnet 4.5

### Complete Development Cycle:
```bash
# 1. Start fresh
git checkout main && git pull origin main

# 2. Create feature branch
git checkout -b feature/my-feature

# 3. Make changes and commit
git add . && git commit -m "Descriptive commit message"
git push origin feature/my-feature

# 4. Create PR on GitHub
# 5. Wait for AI review and address feedback
# 6. Merge when approved

# 7. Clean up (IMPORTANT!)
git checkout main
git pull origin main
git branch -d feature/my-feature
git push origin --delete feature/my-feature
```

### Branch Management Best Practices:
- **Always delete branches after merging** - Keeps repository clean
- **Use descriptive branch names** - `feature/add-login`, `bugfix/fix-api-error`
- **One feature per branch** - Don't mix multiple features
- **Keep branches short-lived** - Merge within a few days

### Commit Message Best Practices:
- **Use present tense** - "Add login feature" not "Added login feature"
- **Be descriptive** - "Fix API error in stock endpoint" not "Fix bug"
- **Keep under 50 characters** for the subject line
- **Use bullet points for details** if needed

## Quick Reference

```bash
# Daily workflow
git checkout main && git pull origin main
git checkout -b feature/my-feature
# ... make changes ...
git add . && git commit -m "Description"
git push origin feature/my-feature
# Create PR on GitHub
# Wait for AI review
# Merge when approved
# Clean up branches
```
