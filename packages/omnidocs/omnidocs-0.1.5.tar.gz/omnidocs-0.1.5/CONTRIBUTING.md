# CONTRIBUTING GUIDELINES


## Versioning Guide

### Version Numbers

We follow [Semantic Versioning](https://semver.org/) (MAJOR.MINOR.PATCH):

- `MAJOR` version when you make incompatible API changes
- `MINOR` version when you add functionality in a backwards compatible manner
- `PATCH` version when you make backwards compatible bug fixes

Example: `1.0.0`, `1.1.0`, `1.1.1`

### How to Release a New Version

1. **Check Current Version**:
```bash
poetry version
```

2. **Bump Version** (choose one):
```bash
poetry version patch  # 0.1.0 -> 0.1.1 (bug fixes)
poetry version minor  # 0.1.1 -> 0.2.0 (new features)
poetry version major  # 0.2.0 -> 1.0.0 (breaking changes)
```

3. **Create Git Tag and Push**:
```bash
# Create tag
git add pyproject.toml
git commit -m "bump: version $(poetry version -s)"
git tag v$(poetry version -s)
git push origin v$(poetry version -s)
```

This will automatically trigger:
- GitHub Release creation
- Package publishing to PyPI

### Common Tasks

#### Remove a Tag (if needed)
```bash
# Delete local tag
git tag -d v0.1.0

# Delete remote tag
git push origin --delete v0.1.0
```

#### Check All Tags
```bash
# List all tags
git tag

# List remote tags
git ls-remote --tags origin
```

#### Build and Publish Locally (if needed)
```bash
# Build package
poetry build

# Publish to PyPI
poetry publish
```

### Version Naming Examples

- Bug fix: `1.0.0` → `1.0.1`
- New feature: `1.0.1` → `1.1.0`
- Breaking change: `1.1.0` → `2.0.0`

## Tips

- Always create a new version for each release
- Never reuse a version number
- Update CHANGELOG.md with your changes
- Test the package locally before releasing
- Make sure all CI tests pass before releasing

## Help

If you're unsure about versioning:
1. Ask in Issues/Discussions
2. Default to a minor version bump for new features
3. When in doubt, bump the minor version