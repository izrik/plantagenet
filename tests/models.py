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


def test_post_tags_from_string_single(ctx):
    tags = plantagenet.Post.tags_from_string('python')
    names = {t.name for t in tags}
    assert names == {'python'}


def test_post_tags_from_string_multiple(ctx):
    tags = plantagenet.Post.tags_from_string('python, flask, web')
    names = {t.name for t in tags}
    assert names == {'python', 'flask', 'web'}


def test_post_tags_from_string_empty(ctx):
    tags = plantagenet.Post.tags_from_string('')
    assert tags == set()


def test_post_tags_from_string_reuses_existing_tag(ctx):
    existing = plantagenet.Tag('python')
    plantagenet.db.session.add(existing)
    plantagenet.db.session.commit()

    tags = plantagenet.Post.tags_from_string('python')
    assert len(tags) == 1
    assert next(iter(tags)).id == existing.id


def test_post_get_next(ctx):
    post1 = plantagenet.Post('P1', 'c', datetime(2024, 1, 1))
    post2 = plantagenet.Post('P2', 'c', datetime(2024, 2, 1))
    plantagenet.db.session.add_all([post1, post2])
    plantagenet.db.session.commit()
    assert post1.get_next() == post2


def test_post_get_prev(ctx):
    post1 = plantagenet.Post('P1', 'c', datetime(2024, 1, 1))
    post2 = plantagenet.Post('P2', 'c', datetime(2024, 2, 1))
    plantagenet.db.session.add_all([post1, post2])
    plantagenet.db.session.commit()
    assert post2.get_prev() == post1


def test_post_get_next_excludes_drafts(ctx):
    post1 = plantagenet.Post('P1', 'c', datetime(2024, 1, 1))
    draft = plantagenet.Post('Draft', 'c', datetime(2024, 2, 1), is_draft=True)
    plantagenet.db.session.add_all([post1, draft])
    plantagenet.db.session.commit()
    assert post1.get_next(include_drafts=False) is None


def test_post_get_next_includes_drafts_when_requested(ctx):
    post1 = plantagenet.Post('P1', 'c', datetime(2024, 1, 1))
    draft = plantagenet.Post('Draft', 'c', datetime(2024, 2, 1), is_draft=True)
    plantagenet.db.session.add_all([post1, draft])
    plantagenet.db.session.commit()
    assert post1.get_next(include_drafts=True) == draft


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
