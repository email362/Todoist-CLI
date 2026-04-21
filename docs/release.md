# Packaging And Release

This project uses `hatchling` through `pyproject.toml`.

## Local Build

Install development dependencies:

```bash
python3 -m pip install -e ".[dev]"
```

Run the full quality gate:

```bash
make check
```

Build source and wheel distributions:

```bash
make build
```

The generated artifacts are written to `dist/`.

## Manual Install From A Built Wheel

```bash
python3 -m pip install dist/todoist_cli-0.1.0-py3-none-any.whl
todoist --version
```

## Release Checklist

1. Confirm `src/todoist_cli/__init__.py` and `pyproject.toml` have the same version.
2. Run `make check`.
3. Run `make build`.
4. Install the built wheel in a clean environment and run `todoist --help`.
5. Create an annotated release tag, for example `git tag -a v0.1.0 -m "Release v0.1.0"`.
6. Push the branch and tag.

Do not commit Todoist tokens, local config files, virtual environments, or build
artifacts.
