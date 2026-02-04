# Building vs_backup

## Prerequisites

- [uv](https://docs.astral.sh/uv/) (for local builds)
- Python 3.14+

## Local build (Windows)

```
build.bat
```

This creates a venv in `.build_venv`, installs PyInstaller, and outputs `dist\vs_backup.exe`.

## CI build

A GitHub Actions workflow builds and publishes the executable automatically when you push a version tag:

```
git tag v1.0.0
git push origin v1.0.0
```

The workflow runs on `windows-latest` and attaches `vs_backup.exe` to the GitHub release.
