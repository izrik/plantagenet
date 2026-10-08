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


def create_legacy_schema(engine):
    # The post table as it was before migrations were introduced
    with engine.connect() as conn:
        conn.execute(text(
            'CREATE TABLE post ('
            'id INTEGER NOT NULL PRIMARY KEY, '
            'title VARCHAR(100), '
            'slug VARCHAR(100), '
            'content TEXT, '
            'summary TEXT, '
            'notes TEXT, '
            'date TIMESTAMP, '
            'last_updated_date TIMESTAMP NOT NULL, '
            'is_draft BOOLEAN NOT NULL DEFAULT FALSE)'
        ))
        conn.commit()


def test_run_migrations_skips_already_applied():
    engine = create_engine('sqlite://')
    create_legacy_schema(engine)
    # Run twice; second run should skip migrations already in schema_migrations
    plantagenet.run_migrations(engine)
    plantagenet.run_migrations(engine)
    # No error means it succeeded; verify the migrations table exists
    with engine.connect() as conn:
        rows = conn.execute(
            text('SELECT version FROM schema_migrations')
        ).fetchall()
    assert len(rows) >= 0


def test_run_migrations_applies_sql_files():
    engine = create_engine('sqlite://')
    create_legacy_schema(engine)
    plantagenet.run_migrations(engine)
    with engine.connect() as conn:
        rows = conn.execute(
            text('SELECT version FROM schema_migrations')
        ).fetchall()
    # The migrations directory has at least one migration
    assert len(rows) > 0


def test_run_migrations_backfills_post_published_date():
    engine = create_engine('sqlite://')
    create_legacy_schema(engine)
    with engine.connect() as conn:
        conn.execute(text(
            "INSERT INTO post (id, title, date, last_updated_date, is_draft) "
            "VALUES (1, 'published', '2020-01-01 00:00:00', "
            "'2020-01-01 00:00:00', FALSE), "
            "(2, 'draft', '2021-01-01 00:00:00', "
            "'2021-01-01 00:00:00', TRUE)"
        ))
        conn.commit()
    plantagenet.run_migrations(engine)
    with engine.connect() as conn:
        rows = dict(conn.execute(
            text('SELECT id, published_date FROM post')
        ).fetchall())
    assert rows[1] == '2020-01-01 00:00:00'
    assert rows[2] is None


def test_run_migrations_stamp_only_records_without_running(ctx):
    engine = app.db.engine
    # The schema is already up to date from create_all, so running the
    # migrations would fail; stamping should only record them
    plantagenet.run_migrations(engine, stamp_only=True)
    with engine.connect() as conn:
        versions = {
            row[0] for row in conn.execute(
                text('SELECT version FROM schema_migrations'))
        }
    assert '0.3' in versions
    assert '0.4' in versions
    # A subsequent normal run has nothing left to apply
    plantagenet.run_migrations(engine)


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
