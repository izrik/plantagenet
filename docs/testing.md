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
- `login` — logs in as the admin by setting the session

## Conventions

- Keep separate test functions for authenticated and unauthenticated cases
  rather than parametrizing them.
- Add tests for new behavior and bug fixes.
- Test files are not prefixed with `test_` — all `.py` files in `tests/` are
  collected per `pytest.ini`.

## Authentication in Tests

The admin user password is set via the `Option` table (`hashed_password` key).
The `login` fixture handles this automatically for tests that need
authenticated access.
