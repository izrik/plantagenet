# Testing

## Running Tests

Run the full check suite before committing; this is what CI runs:

```sh
./run_tests_with_coverage.sh
```

It runs, in order: pytest under coverage, `flake8 plantagenet.py tests/`,
`bandit plantagenet.py`, `shellcheck`, `pymarkdown scan README.md`, and
`pip-audit`. For a quick loop, run just `pytest tests/` from the project root.

## Test Fixtures

Use the fixtures in `tests/conftest.py`:

- `ctx` — app with in-memory SQLite and a pushed app context
- `cl` — Flask test client
- `make_user` — creates and saves a `User` (defaults: `user@example.com`,
  password `password123`, not an administrator)
- `admin_user` — an administrator, `admin@example.com`
- `regular_user` — a non-administrator, `user@example.com`
- `login` — logs a user in by setting the session; defaults to `admin_user`,
  or pass another user, e.g. `login(regular_user)`

## Conventions

- Keep separate test functions for authenticated and unauthenticated cases
  rather than parametrizing them.
- Add tests for new behavior and bug fixes.
- Test files are not prefixed with `test_` — all `.py` files in `tests/` are
  collected per `pytest.ini`.

## Authentication in Tests

Each user has their own bcrypt-hashed password in the `users` table. The
`login` fixture creates an administrator and puts their id in the session, so
tests that need authenticated access just call `login()`. For a view that
administrators and regular users should see differently, write both a
`login()` case and a `login(regular_user)` case.
