# CodeCrew Example Project

This is an example project demonstrating CodeCrew usage for a Task Management API.

## Getting Started

1. Initialize the CodeCrew project:
```bash
codecrew init --project task-api --spec spec.md --brd brd.md --prd prd.md --userstories userstories.md --checklist checklist.md
```

2. Deploy the development team:
```bash
codecrew deploy --project task-api
```

3. Monitor progress:
```bash
codecrew status --project task-api
```

## Project Files

- `spec.md` - Technical specification with requirements and API design
- `brd.md` - Business Requirements Document with business context and objectives
- `prd.md` - Product requirements with business goals and success metrics
- `userstories.md` - User stories and acceptance criteria
- `checklist.md` - Project checklist and deliverables tracking

## Next Steps

1. Set up GitHub repository: `codecrew github setup`
2. Configure development environment
3. Launch Claude Code agents using the generated scripts
4. Begin development following the GitHub workflow

Happy coding with CodeCrew! 🚀
