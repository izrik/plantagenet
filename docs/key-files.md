# Key Files

A detailed file-by-file map of the plantagenet repository.

## Application

- `plantagenet.py` — the entire application: config, CLI argument parsing,
  models (`Post`, `Tag`, `Page`, `Option`), view functions, migrations runner,
  and the `create_app()` factory. A module-level `app = create_app()` is
  created on import, and `db.create_all()` plus `run_migrations()` run at
  import time.

## Templates and Static Files

- `templates/` — Jinja2 templates (Bootstrap 3 styling); `base.html` is the
  layout used by every page.
- `static/` — CSS (`bootstrap.min.css`, `plantagenet.css`).

## Database Migrations

- `migrations/` — versioned SQL migrations (`vX.Y.sql` / `vX.Y.Z.sql`),
  applied automatically at startup and tracked in `schema_migrations`. See
  `migrations/README.md`. Migration SQL must work on SQLite, MySQL, and
  PostgreSQL (e.g. use `TIMESTAMP`, not `DATETIME`).

## Tests

- `tests/` — pytest suite. Note that `pytest.ini` sets `python_files = *.py`,
  so every `.py` file in `tests/` is collected (files are not named
  `test_*.py`).

## Docker

- `Dockerfile`, `docker_start.sh` — container image running gunicorn on port
  8080.

## CI/CD

- `.github/workflows/ci.yml` — CI; runs `run_tests_with_coverage.sh` on Python
  3.12.
- `.travis.yml` — legacy CI configuration (superseded by GitHub Actions).
