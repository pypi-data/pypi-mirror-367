# Version Bumping with CodeCrew

CodeCrew uses `bump-my-version` for automated version management. This document explains how to use the version bumping system.

## 🔧 Configuration

The version bumping is configured in `pyproject.toml` under the `[tool.bumpversion]` section:

- **Current version**: Tracked in both `codecrew/__init__.py` and `pyproject.toml`
- **Version format**: Semantic versioning (major.minor.patch)
- **Git integration**: Automatically commits and tags new versions
- **File updates**: Updates version in both Python package and config files

## 🚀 Usage

### Using Hatch Scripts (Recommended)

```bash
# Show current version and possible bumps
hatch run show-bump

# Show detailed configuration
hatch run show-version

# Bump patch version (1.0.0 → 1.0.1)
hatch run bump-patch

# Bump minor version (1.0.0 → 1.1.0)
hatch run bump-minor

# Bump major version (1.0.0 → 2.0.0)
hatch run bump-major
```

### Using bump-my-version Directly

```bash
# Show what versions would be created
uv run bump-my-version show-bump

# Dry run (see what would change without making changes)
uv run bump-my-version bump --dry-run patch

# Actually bump the version
uv run bump-my-version bump patch
uv run bump-my-version bump minor
uv run bump-my-version bump major
```

### Using uv with development environment

```bash
# Install development dependencies (includes bump-my-version)
uv sync --extra dev

# Use bump-my-version
uv run bump-my-version bump patch
```

## 📋 What Happens During a Version Bump

1. **Version Parsing**: Reads current version from `pyproject.toml`
2. **File Updates**: Updates version in:
   - `codecrew/__init__.py` (`__version__ = "x.y.z"`)
   - `pyproject.toml` (`current_version = "x.y.z"`)
3. **Git Operations**:
   - Stages the changed files
   - Commits with message: `Bump version: 1.0.0 → 1.0.1`
   - Creates git tag: `v1.0.1`

## 🎯 Version Types

- **Patch** (`1.0.0 → 1.0.1`): Bug fixes, small improvements
- **Minor** (`1.0.0 → 1.1.0`): New features, backwards compatible
- **Major** (`1.0.0 → 2.0.0`): Breaking changes, major updates

## 🔍 Verification

After bumping a version, verify the changes:

```bash
# Check the version was updated
cat codecrew/__init__.py | grep __version__

# Check git log
git log --oneline -5

# Check git tags
git tag --sort=-version:refname | head -5

# Verify the package version
uv run python -c "import codecrew; print(codecrew.__version__)"
```

## 🚨 Important Notes

- **Clean working directory**: Ensure no uncommitted changes before bumping
- **Git repository**: Must be in a git repository for tagging to work
- **Permissions**: Ensure you have permission to push tags if using remote repository
- **Testing**: Always test after version bumps to ensure everything works

## 🛠️ Troubleshooting

### "Working directory is dirty"
```bash
# Check what files are modified
git status

# Commit or stash changes before bumping
git add . && git commit -m "Prepare for version bump"
```

### "No git repository"
```bash
# Initialize git repository
git init
git add .
git commit -m "Initial commit"
```

### Version not updating in package
```bash
# Reinstall the package after version bump
uv tool uninstall codecrew
uv tool install .
```

## 📚 Advanced Usage

### Custom commit messages
```bash
uv run bump-my-version bump --message "Release version {new_version}" patch
```

### Skip git operations
```bash
uv run bump-my-version bump --no-commit --no-tag patch
```

### Bump specific files only
```bash
uv run bump-my-version bump --no-configured-files patch codecrew/__init__.py
```

For more advanced options, see the [bump-my-version documentation](https://github.com/callowayproject/bump-my-version).
