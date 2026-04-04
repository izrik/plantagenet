import types

import pytest

import plantagenet
from plantagenet import app


def _fake_args(**kwargs):
    defaults = dict(
        create_db=False,
        hash_password=None,
        count_posts=False,
        reset_slug=None,
        set_date=None,
        set_last_updated_date=None,
        reset_summary=None,
        set_option=None,
        clear_option=None,
    )
    defaults.update(kwargs)
    return types.SimpleNamespace(**defaults)


def _set_args(monkeypatch, **kwargs):
    monkeypatch.setattr(plantagenet, 'args', _fake_args(**kwargs),
                        raising=False)


def test_run_create_db(ctx, monkeypatch):
    _set_args(monkeypatch, create_db=True)
    plantagenet.run()


def test_run_hash_password(ctx, monkeypatch):
    _set_args(monkeypatch, hash_password='mypassword')
    plantagenet.run()


def test_run_count_posts(ctx, monkeypatch):
    _set_args(monkeypatch, count_posts=True)
    plantagenet.run()


def test_run_reset_slug(ctx, monkeypatch):
    from datetime import datetime
    post = plantagenet.Post('My Post', 'content', datetime(2024, 1, 1))
    app.db.session.add(post)
    app.db.session.commit()
    _set_args(monkeypatch, reset_slug=str(post.id))
    plantagenet.run()


def test_run_reset_slug_not_found(ctx, monkeypatch):
    _set_args(monkeypatch, reset_slug='999')
    plantagenet.run()


def test_run_set_option_new(ctx, monkeypatch):
    _set_args(monkeypatch, set_option=('mykey', 'myvalue'))
    plantagenet.run()


def test_run_set_option_existing(ctx, monkeypatch):
    opt = plantagenet.Option('mykey', 'oldvalue')
    app.db.session.add(opt)
    app.db.session.commit()
    _set_args(monkeypatch, set_option=('mykey', 'newvalue'))
    plantagenet.run()


def test_run_clear_option(ctx, monkeypatch):
    opt = plantagenet.Option('mykey', 'value')
    app.db.session.add(opt)
    app.db.session.commit()
    _set_args(monkeypatch, clear_option='mykey')
    plantagenet.run()


def test_run_clear_option_not_found(ctx, monkeypatch):
    _set_args(monkeypatch, clear_option='nonexistent')
    with pytest.raises(SystemExit):
        plantagenet.run()
