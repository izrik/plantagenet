from datetime import datetime

import plantagenet


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
