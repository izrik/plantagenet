# CLAUDE.md

Guidance for AI coding agents (and humans) working in this repository.
`AGENTS.md` is a symlink to this file; edit `CLAUDE.md` only.

## Project Overview

Plantagenet is a Python blogging system built on Flask, Flask-SQLAlchemy,
Flask-Login, and Flask-Bcrypt. Posts and pages are written in GitHub-flavored
Markdown and rendered with `pycmarkgfm`. There is a single admin user whose
bcrypt-hashed password is stored in the `Option` table under `hashed_password`.

## Commands

```sh
# Setup
python3 -m venv venv && . venv/bin/activate
pip install -r requirements.txt -r dev_requirements.txt

# Run locally (defaults to 127.0.0.1:1177)
python plantagenet.py --db-uri sqlite:///plantagenet.db --create-db
python plantagenet.py --db-uri sqlite:///plantagenet.db --debug

# Run all checks (CI runs this)
./run_tests_with_coverage.sh

# Quick test loop
pytest tests/

# Lint only
flake8 plantagenet.py tests/
```

## Architecture

Single-module Flask application (`plantagenet.py`) containing:

- **Config class** — settings from `PLANTAGENET_*` env vars
- **Models** — `Post`, `Tag`, `Page`, `Option` (SQLAlchemy)
- **View functions** — routes registered via `app.add_url_rule()` in `create_app()`
- **Migrations runner** — applies SQL files from `migrations/` at startup

Templates use Bootstrap 3 (`templates/`), static assets in `static/`.

## Code Style

- Follow PEP 8; all code must pass `flake8` (79-column lines) and `bandit`.
- Keep the single-module structure of `plantagenet.py` unless there is a
  strong reason to split it.
- Put query logic in model methods (repository-style); keep views thin.
- Templates use Bootstrap 3 classes; flash messages render in `base.html`.
- Schema changes require a new migration with a higher version number.
- Dependencies are pinned exactly in `requirements.txt` and
  `dev_requirements.txt`.

## Development Workflow

1. **Branch** — create a branch for your work (use hyphens, not slashes)
2. **Implement** — make changes following the code style above
3. **Test** — run `./run_tests_with_coverage.sh` before committing
4. **Changelog** — add an entry under `## [Unreleased]` in
   [CHANGELOG.md](CHANGELOG.md) for anything a user or operator would
   notice: a new command or route, a changed default, a new environment
   variable, a fixed bug. Internal refactors with no outward effect need
   no entry.
5. **Commit** — short, imperative, sentence-style messages ending with a
   period (e.g. `Add admin page to edit site name.`)
6. **PR** — open pull request against `master`; reference issues with
   `Closes #N`
7. **Review** — address feedback, push fixes

## Further Documentation

- [Changelog](CHANGELOG.md) — notable changes, newest first
- [Key Files](docs/key-files.md) — file-by-file map of the repository
- [Configuration](docs/configuration.md) — environment variables and settings
- [Testing](docs/testing.md) — test fixtures and conventions
- [Migrations](migrations/README.md) — database migration format and workflow
