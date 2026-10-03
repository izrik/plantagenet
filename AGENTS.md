# AGENTS.md

Guidance for AI coding agents (and humans) working in this repository.
`CLAUDE.md` is a symlink to this file; edit `AGENTS.md` only.

## Project Overview

Plantagenet is a small Python blogging system built on Flask, Flask-SQLAlchemy,
Flask-Login, and Flask-Bcrypt. Posts and pages are written in GitHub-flavored
Markdown and rendered with `pycmarkgfm`. There is a single admin user whose
bcrypt-hashed password is stored in the `Option` table under
`hashed_password`.

## Repository Layout

- `plantagenet.py` - the entire application: config, CLI argument parsing,
  models (`Post`, `Tag`, `Page`, `Option`), view functions, migrations runner,
  and the `create_app()` factory. A module-level `app = create_app()` is
  created on import, and `db.create_all()` plus `run_migrations()` run at
  import time.
- `templates/` - Jinja2 templates (Bootstrap 3 styling); `base.html` is the
  layout used by every page.
- `static/` - CSS (`bootstrap.min.css`, `plantagenet.css`).
- `migrations/` - versioned SQL migrations (`vX.Y.sql` / `vX.Y.Z.sql`),
  applied automatically at startup and tracked in `schema_migrations`. See
  `migrations/README.md`. Migration SQL must work on SQLite, MySQL, and
  PostgreSQL (e.g. use `TIMESTAMP`, not `DATETIME`).
- `tests/` - pytest suite. Note that `pytest.ini` sets `python_files = *.py`,
  so every `.py` file in `tests/` is collected (files are not named
  `test_*.py`).
- `Dockerfile`, `docker_start.sh` - container image running gunicorn on port
  8080.
- `.github/workflows/ci.yml` - CI; runs `run_tests_with_coverage.sh` on Python
  3.12. (`.travis.yml` is legacy.)

## Configuration

Settings live on the `Config` class and come from `PLANTAGENET_*` environment
variables, overridable by command-line flags (see `--help`). Notable ones:
`PLANTAGENET_DB_URI` / `PLANTAGENET_DB_URI_FILE` (defaults to in-memory
SQLite), `PLANTAGENET_SECRET_KEY`, `PLANTAGENET_CUSTOM_TEMPLATES`,
`PLANTAGENET_EXTERN_ROOT`, and `PLANTAGENET_EXTRA_LINKS`. Some settings
(site name, site URL, author, extra links) can also be overridden at runtime
via the `Option` table, which takes precedence over `Config`.

## Development Setup

```sh
python3 -m venv venv
. venv/bin/activate
pip install -r requirements.txt -r dev_requirements.txt
```

Run locally (defaults to `127.0.0.1:1177`):

```sh
python plantagenet.py --db-uri sqlite:///plantagenet.db --create-db
python plantagenet.py --db-uri sqlite:///plantagenet.db --debug
```

Logging in requires an initial admin password: run
`python plantagenet.py --hash-password PASSWORD` (it prints the hash as a
Python bytes literal, `b'...'`; use the string inside the quotes), then
`python plantagenet.py --set-option hashed_password HASH`. After that, the
password can be changed from the `/admin` page.

## Testing and Checks

Run the full check suite before committing; this is what CI runs:

```sh
./run_tests_with_coverage.sh
```

It runs, in order: pytest under coverage, `flake8 plantagenet.py tests/`,
`bandit plantagenet.py`, `shellcheck`, `pymarkdown scan README.md`, and
`pip-audit`. For a quick loop, run just `pytest` (or `pytest tests/post.py`).

Testing conventions:

- Use the fixtures in `tests/conftest.py`: `ctx` (app with in-memory SQLite
  and a pushed app context), `cl` (test client), and `login` (logs in as the
  admin by setting the session).
- Keep separate test functions for authenticated and unauthenticated cases
  rather than parametrizing them.
- Add tests for new behavior and bug fixes.

## Coding Conventions

- Follow PEP 8; all code and tests must pass `flake8` (79-column lines) and
  `bandit`.
- Keep the single-module structure of `plantagenet.py` unless there is a
  strong reason to split it. Register new routes in `create_app()` with
  `app.add_url_rule(...)` rather than decorators.
- Put query logic in model methods (repository-style) and keep view
  functions thin.
- Templates use Bootstrap 3 classes; flash messages are rendered in
  `base.html`, and the `error` category maps to `alert-danger`.
- Schema changes require a new migration file with a higher version number
  than any existing one; never edit a migration that has already shipped.
- Dependencies are pinned exactly in `requirements.txt` and
  `dev_requirements.txt`.

## Commits and Pull Requests

- Write short, imperative, sentence-style commit messages ending with a
  period (e.g. `Add admin page to edit site name and password.`).
- Keep commits focused; open pull requests against `master` and reference
  the issue they close (e.g. `Closes #93`).
