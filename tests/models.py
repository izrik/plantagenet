from datetime import datetime

import pytest

import plantagenet


def test_post_validate_title_valid(ctx):
    plantagenet.Post.validate_title('Hello World')


def test_post_validate_title_empty_raises(ctx):
    with pytest.raises(Exception):
        plantagenet.Post.validate_title('')


def test_post_validate_title_whitespace_only_raises(ctx):
    with pytest.raises(Exception):
        plantagenet.Post.validate_title('   ')


def test_page_validate_title_valid(ctx):
    plantagenet.Page.validate_title('Hello World')


def test_page_validate_title_empty_raises(ctx):
    with pytest.raises(Exception):
        plantagenet.Page.validate_title('')


def test_page_validate_title_whitespace_only_raises(ctx):
    with pytest.raises(Exception):
        plantagenet.Page.validate_title('   ')


def test_user_get_name(ctx):
    user = plantagenet.User('alice', 'alice@example.com')
    assert user.get_name() == 'alice'


def test_page_content_setter_none(ctx):
    page = plantagenet.Page('My Page', None, datetime(2024, 1, 1))
    assert page.content == ''


def test_options_get_siteurl(ctx):
    url = plantagenet.Options.get_siteurl()
    assert url is not None


def test_options_seq(ctx):
    gen = plantagenet.Options.seq()
    assert next(gen) == 0
    assert next(gen) == 1
    assert next(gen) == 2
