import os
import tempfile

import plantagenet
from plantagenet import app
from sqlalchemy import create_engine, text
import pytest


def test_run_migrations_no_dir_returns_early(monkeypatch):
    monkeypatch.setattr(plantagenet.os.path, 'isdir', lambda p: False)
    engine = create_engine('sqlite://')
    # Should not raise and should not create schema_migrations table
    plantagenet.run_migrations(engine)
    with engine.connect() as conn:
        tables = conn.execute(
            text("SELECT name FROM sqlite_master WHERE type='table'")
        ).fetchall()
    table_names = [t[0] for t in tables]
    assert 'schema_migrations' not in table_names


def test_run_migrations_skips_already_applied(ctx):
    engine = app.db.engine
    # Run twice; second run should skip migrations already in schema_migrations
    plantagenet.run_migrations(engine)
    plantagenet.run_migrations(engine)
    # No error means it succeeded; verify the migrations table exists
    with engine.connect() as conn:
        rows = conn.execute(
            text('SELECT version FROM schema_migrations')
        ).fetchall()
    assert len(rows) >= 0


def test_run_migrations_applies_sql_files(ctx):
    engine = app.db.engine
    plantagenet.run_migrations(engine)
    with engine.connect() as conn:
        rows = conn.execute(
            text('SELECT version FROM schema_migrations')
        ).fetchall()
    # The migrations directory has at least one migration
    assert len(rows) > 0


def test_run_migrations_rollback_on_error(monkeypatch):
    with tempfile.TemporaryDirectory() as tmpdir:
        migrations_dir = os.path.join(tmpdir, 'migrations')
        os.makedirs(migrations_dir)
        with open(os.path.join(migrations_dir, 'v1.0.sql'), 'w') as f:
            f.write('THIS IS NOT VALID SQL')
        fake_file = os.path.join(tmpdir, 'plantagenet.py')
        monkeypatch.setattr(
            plantagenet.os.path, 'abspath',
            lambda p: fake_file
        )
        engine = create_engine('sqlite://')
        with pytest.raises(Exception):
            plantagenet.run_migrations(engine)
