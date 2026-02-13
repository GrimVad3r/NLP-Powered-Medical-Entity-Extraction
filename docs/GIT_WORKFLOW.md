# Git Workflow & Branching Strategy

**Medical Intelligence Platform v2.0 - Production-Grade Development**

---

## 🌳 Branch Structure

### Main Branches

```
main (production)
  └── develop (integration branch)
       └── feature/* (feature branches)
```

**Rules:**
- `main`: Production-ready code only
- `develop`: Integration and testing branch
- `feature/*`: Individual feature branches
- Never commit directly to `main` or `develop`

---

## 📋 Branch Naming Convention

```
feature/branch-{N}-{component}/{task-name}
```

**Examples:**
```
feature/branch-1-core/config-management
feature/branch-1-core/logging-system
feature/branch-2-extraction/telegram-client
feature/branch-3-nlp/medical-ner
feature/branch-3-nlp/entity-linking
feature/branch-4-database/orm-models
feature/branch-5-transformation/dbt-integration
feature/branch-6-api/fastapi-setup
feature/branch-7-dashboard/wordcloud-feature
feature/branch-8-utilities/decorators
```

---

## 🔄 Git Workflow Process

### 1. Start a New Feature

```bash
# Update develop branch
git checkout develop
git pull origin develop

# Create feature branch from develop
git checkout -b feature/branch-1-core/config-management

# Or use git flow (if installed)
git flow feature start branch-1-core/config-management
```

### 2. Make Changes

```bash
# Make your changes
nano src/core/config.py

# Stage changes
git add src/core/config.py

# Or stage all changes
git add .

# Commit with descriptive message
git commit -m "feat(core): add configuration management system"
```

### 3. Commit Message Format

Follow Conventional Commits:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Code style (formatting, missing semicolons)
- `refactor`: Code refactoring
- `perf`: Performance improvement
- `test`: Adding tests
- `chore`: Build, dependencies, tooling

**Scopes:**
- `core`: Core utilities
- `extraction`: Data extraction
- `nlp`: NLP pipeline
- `database`: Database layer
- `transformation`: Data transformation
- `api`: REST API
- `dashboard`: Dashboard
- `utils`: Utilities

**Examples:**

```bash
# Simple feature
git commit -m "feat(core): add configuration management system"

# With body
git commit -m "feat(nlp): implement medical entity recognition

- Add spaCy medical NER
- Implement rule-based extraction
- Add entity deduplication logic

Resolves #123"

# Bug fix
git commit -m "fix(extraction): handle telegram API timeout errors"

# Documentation
git commit -m "docs(api): add API endpoint documentation"
```

---

## 📤 Create Pull Request

```bash
# Push feature branch to remote
git push origin feature/branch-1-core/config-management

# Go to GitHub and create PR
# - Base branch: develop
# - Compare branch: feature/branch-1-core/config-management
```

### PR Description Template

```markdown
## Description
Briefly describe what this PR does.

## Changes
- Added configuration management module
- Implemented environment variable validation
- Created settings class with type hints

## Type of Change
- [ ] New feature
- [x] Bug fix
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [x] Unit tests added
- [x] Integration tests added
- [x] Manual testing completed

## Checklist
- [x] Code follows style guidelines
- [x] Documentation updated
- [x] Tests added/updated
- [x] No new warnings generated
- [x] Commit messages follow convention

## Related Issues
Closes #123, #124
```

---

## ✅ Code Review Process

### Before Merging

1. **All tests pass**
   ```bash
   pytest tests/ -v
   ```

2. **Code quality checks**
   ```bash
   black --check src/ tests/
   isort --check-only src/ tests/
   flake8 src/ tests/
   mypy src/ --strict
   ```

3. **Coverage maintained**
   ```bash
   pytest tests/ --cov=src --cov-report=term-missing
   ```

4. **Documentation updated**
   - Update README if needed
   - Add docstrings
   - Update API docs

### Merge Feature Branch

```bash
# Switch to develop
git checkout develop
git pull origin develop

# Merge feature branch
git merge feature/branch-1-core/config-management

# Delete feature branch
git branch -d feature/branch-1-core/config-management
git push origin --delete feature/branch-1-core/config-management
```

---

## 🎯 Branch-Specific Commit Examples

### BRANCH-1: Core Utilities

```bash
git commit -m "feat(core): add configuration management system"
git commit -m "feat(core): implement structured logging with rotation"
git commit -m "feat(core): add custom exception hierarchy"
git commit -m "feat(core): implement input validators"
git commit -m "test(core): add configuration validation tests"
```

### BRANCH-2: Extraction

```bash
git commit -m "feat(extraction): implement Telegram API client wrapper"
git commit -m "feat(extraction): add channel scraper with error handling"
git commit -m "feat(extraction): implement message handler with filtering"
git commit -m "feat(extraction): add media downloader with retry logic"
git commit -m "test(extraction): add telegram client tests"
```

### BRANCH-3: NLP Pipeline

```bash
git commit -m "feat(nlp): integrate spaCy medical entity recognition"
git commit -m "feat(nlp): implement medical text classifier"
git commit -m "feat(nlp): add entity linking with fuzzy matching"
git commit -m "feat(nlp): create unified message processor pipeline"
git commit -m "feat(nlp): implement word cloud generation"
git commit -m "test(nlp): add NER extraction tests"
```

### BRANCH-4: Database

```bash
git commit -m "feat(database): add SQLAlchemy ORM models"
git commit -m "feat(database): implement CRUD operations"
git commit -m "feat(database): add database connection pooling"
git commit -m "feat(database): implement migration system"
git commit -m "test(database): add database operation tests"
```

### BRANCH-5: Transformation

```bash
git commit -m "feat(transformation): integrate dbt orchestration"
git commit -m "feat(transformation): implement data cleaning logic"
git commit -m "feat(transformation): add data quality checks"
git commit -m "feat(transformation): implement aggregation functions"
```

### BRANCH-6: API

```bash
git commit -m "feat(api): setup FastAPI application"
git commit -m "feat(api): add product endpoints"
git commit -m "feat(api): add NLP processing endpoints"
git commit -m "feat(api): add analytics endpoints"
git commit -m "feat(api): implement request/response middleware"
```

### BRANCH-7: Dashboard

```bash
git commit -m "feat(dashboard): setup Streamlit application"
git commit -m "feat(dashboard): add word cloud visualization"
git commit -m "feat(dashboard): implement product analytics page"
git commit -m "feat(dashboard): add NLP insights page"
git commit -m "feat(dashboard): implement reusable components"
```

### BRANCH-8: Utilities

```bash
git commit -m "feat(utils): add retry and caching decorators"
git commit -m "feat(utils): implement helper functions"
git commit -m "feat(utils): add constants and enums"
git commit -m "feat(utils): add text processing utilities"
```

---

## 🔀 Merge to Main

After develop is stable:

```bash
# Create release branch
git checkout -b release/v2.1.0 develop

# Update version numbers
nano src/core/config.py  # Update app_version

# Commit version bump
git commit -m "chore: bump version to 2.1.0"

# Create tag
git tag -a v2.1.0 -m "Release version 2.1.0"

# Switch to main
git checkout main
git pull origin main

# Merge release
git merge --no-ff release/v2.1.0

# Push to main
git push origin main
git push origin v2.1.0

# Merge back to develop
git checkout develop
git merge --no-ff release/v2.1.0
git push origin develop

# Delete release branch
git branch -d release/v2.1.0
git push origin --delete release/v2.1.0
```

---

## 📊 Viewing History

```bash
# View branch history
git log --oneline --graph --all

# View specific branch
git log origin/develop --oneline -10

# View with detailed info
git log --format=fuller

# View file history
git log -p src/core/config.py

# View tags
git tag -l

# Show tag details
git show v2.1.0
```

---

## 🐛 Hotfixes

For urgent production fixes:

```bash
# Create hotfix branch from main
git checkout -b hotfix/security-patch main

# Make fix
nano src/core/security.py

# Commit
git commit -m "fix(security): patch authentication vulnerability"

# Merge to main
git checkout main
git merge --no-ff hotfix/security-patch
git push origin main

# Merge back to develop
git checkout develop
git merge --no-ff hotfix/security-patch
git push origin develop

# Tag
git tag -a v2.0.1 -m "Hotfix release"
git push origin v2.0.1

# Delete hotfix branch
git branch -d hotfix/security-patch
```

---

## ⚙️ Git Configuration

```bash
# Set your identity
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Set default editor
git config --global core.editor "nano"

# Enable color output
git config --global color.ui true

# Create aliases
git config --global alias.co checkout
git config --global alias.br branch
git config --global alias.ci commit
git config --global alias.st status
git config --global alias.log-pretty "log --oneline --graph --all"

# View config
git config --list
```

---

## 🔗 Integration with CI/CD

### GitHub Actions Workflow

```yaml
name: Test on Push

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - run: pip install -r requirements.txt
      - run: pytest tests/ --cov=src
      - run: flake8 src/
      - run: mypy src/ --strict
```

---

## 📝 Useful Git Commands

```bash
# Status
git status

# Stash changes
git stash
git stash pop

# Rebase (clean history)
git rebase -i HEAD~3

# Squash commits
git rebase -i develop
# Mark commits as 'squash'

# Undo last commit
git reset --soft HEAD~1

# Amend last commit
git commit --amend --no-edit

# Cherry-pick commit
git cherry-pick <commit-sha>

# Show differences
git diff
git diff --staged

# Find commits
git log --grep="feat"
git log --author="name"
```

---

## ✨ Best Practices

1. **Keep commits small and focused**
   - One logical change per commit
   - Easy to review and understand

2. **Write clear commit messages**
   - Use imperative mood ("add" not "added")
   - First line: what changed
   - Body: why it changed

3. **Pull before pushing**
   ```bash
   git pull --rebase origin develop
   ```

4. **Never force push to develop/main**
   ```bash
   # ❌ Don't do this
   git push --force origin develop
   ```

5. **Delete merged branches**
   ```bash
   git branch --merged | grep -v develop | xargs git branch -d
   ```

6. **Review your own PR first**
   - Read the changes you made
   - Check tests pass
   - Verify no commented-out code

---

**Last Updated: 2025-02-13**
**Maintained by: Boris (Claude Code)**