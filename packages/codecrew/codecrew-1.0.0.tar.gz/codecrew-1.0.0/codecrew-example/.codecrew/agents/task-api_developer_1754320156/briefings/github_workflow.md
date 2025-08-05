# GitHub Workflow Guide for Developer

## Repository Information
- Repository: Not connected
- Your Role: Developer
- Current Branch: unknown

## Essential GitHub Commands

### Check Your Work
```bash
# See your assigned issues
gh issue list --assignee @me

# See your open PRs  
gh pr list --author @me

# See PRs awaiting your review
gh pr list --review-requested @me
```

### Create New Work
```bash
# Create feature branch
git checkout -b feature/[issue-number]-[description]

# Make commits with conventional format
git commit -m "feat(scope): description

Details about the change

Refs: #[issue-number]"

# Create PR
gh pr create --title "Title" --body "Description

Closes #[issue-number]"
```

### Quality Standards
- Commit every 30 minutes maximum
- Reference issue numbers in commits
- Use conventional commit format
- Test coverage ≥80%
- All CI checks must pass
- Get code review approval before merge

## Communication Protocol
- Update status.json every 30 minutes
- Document progress in progress/current.md
- Report blockers in blockers.md immediately
- Don't stay blocked longer than 10 minutes
