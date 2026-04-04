from datetime import datetime

import pytest

import plantagenet
from plantagenet import app

pytestmark = pytest.mark.usefixtures('ctx')


def test_init():
    # when a Post is created
    post = plantagenet.Post('title', 'content', datetime(2017, 1, 1))

    # then the title is the same as what was passed to the constructor
    assert post.title == 'title'

    # then the content is the same as what was passed to the constructor
    assert post.content == 'content'

    # then the date is the same as what was passed to the constructor
    assert post.date == datetime(2017, 1, 1)


def test_init_optional_arg_is_draft():
    # when a Post is created
    post = plantagenet.Post('title', 'content', datetime(2017, 1, 1))

    # then optional argument "is_draft" have its default value of False
    assert not post.is_draft


def test_init_set_is_draft():
    # when a Post is created
    post = plantagenet.Post('title', 'content', datetime(2017, 1, 1), True)

    # then the is_draft field is the same as what was passed to the constructor
    assert post.is_draft


def test_init_set_is_draft_named():
    # when a Post is created
    post = plantagenet.Post('title', 'content', datetime(2017, 1, 1),
                            is_draft=True)

    # then the is_draft field is the same as what was passed to the constructor
    assert post.is_draft


def test_init_optional_arg_notes():
    # when a Post is created
    post = plantagenet.Post('title', 'content', datetime(2017, 1, 1))

    # then optional argument "notes" have its default value of None
    assert post.notes is None


def test_init_set_notes():
    # when a Post is created
    post = plantagenet.Post('title', 'content', datetime(2017, 1, 1),
                            False, 'notes')

    # then the notes field is the same as what was passed to the constructor
    assert post.notes == 'notes'


def test_init_set_notes_named():
    # when a Post is created
    post = plantagenet.Post('title', 'content', datetime(2017, 1, 1),
                            False, notes='notes')

    # then the notes field is the same as what was passed to the constructor
    assert post.notes == 'notes'


def test_init_set_slug_from_simple_title():
    # when a Post with a simple title is created
    post = plantagenet.Post('title', 'content', datetime(2017, 1, 1))

    # then the post's slug is set
    assert post.slug == 'title'


def test_init_set_slug_from_title_with_spaces():
    # when a Post with a simple title is created
    post = plantagenet.Post('title  one', 'content', datetime(2017, 1, 1))

    # then the post's slug is set, with consecutive spaces replaced by a
    # single hyphen
    assert post.slug == 'title-one'


def test_init_set_slug_from_title_with_leading_spaces():
    # when a Post with a simple title is created
    post = plantagenet.Post(' title', 'content', datetime(2017, 1, 1))

    # then the post's slug is set, with leading spaces removed
    assert post.slug == 'title'


def test_init_set_slug_from_title_with_trailing_spaces():
    # when a Post with a simple title is created
    post = plantagenet.Post('title ', 'content', datetime(2017, 1, 1))

    # then the post's slug is set, with trailing spaces removed
    assert post.slug == 'title'


def test_init_set_slug_from_title_with_non_word_characters():
    # when a Post with a simple title is created
    post = plantagenet.Post('title ! $,()', 'content', datetime(2017, 1, 1))

    # then the post's slug is set, with non-word chars removed
    assert post.slug == 'title'


def test_init_set_slug_from_title_with_upper_case():
    # when a Post with a simple title is created
    post = plantagenet.Post('TITLEtitletItLe', 'content', datetime(2017, 1, 1))

    # then the post's slug is set
    assert post.slug == 'titletitletitle'


def test_init_set_summary_from_content():
    # when a Post is created
    post = plantagenet.Post('title', 'content', datetime(2017, 1, 1))

    # then the post's summary is set from the content
    assert post.summary == 'content'


def test_init_set_summary_from_content_truncated():
    # when a Post is created from content with length == 100
    content = ('12345678901234567890123456789012345678901234567890'
               '12345678901234567890123456789012345678901234567890')  # 100
    post = plantagenet.Post('title', content, datetime(2017, 1, 1))

    # then the post's summary is set from the content without modification
    assert post.summary == content

    # when a Post is created from content with length > 100
    content2 = ('12345678901234567890123456789012345678901234567890'
                '123456789012345678901234567890123456789012345678901')  # 101
    expected = ('12345678901234567890123456789012345678901234567890'
                '12345678901234567890123456789012345678901234567890...')
    post = plantagenet.Post('title', content2, datetime(2017, 1, 1))

    # then the post's summary is set from the truncated content
    assert post.summary == expected


def test_init_set_last_updated_date():
    post = plantagenet.Post('title', 'content', datetime(2017, 1, 1))

    # then the post's last_updated_date is set from the date
    assert post.last_updated_date == datetime(2017, 1, 1)


def test_summarize_consecutive_spaces_are_condensed():
    # when
    result = plantagenet.Post.summarize('one  two')

    # then
    assert result == 'one two'


def test_summarize_html_tags_are_removed():
    # when
    result = plantagenet.Post.summarize('<a href="/">Home</a>')

    # then
    assert result == 'Home'


def test_summarize_punctuation_has_added_space():
    # when
    result = plantagenet.Post.summarize('one,two.three?four!five')

    # then
    assert result == 'one, two. three? four! five'


def test_summarize_wordish_chars_are_kept():
    # when
    result = plantagenet.Post.summarize('Something,.?!')

    # then
    assert result == 'Something, . ? ! '


def test_summarize_non_wordish_chars_are_removed():
    # when
    result = plantagenet.Post.summarize(
        'Something :@#$%^&*()[]-_=+[]{}\\|;:\'"/<>')

    # then
    assert result == 'Something '


def test_summarize_long_values_are_truncated():
    # when a string has length == 100
    content = ('12345678901234567890123456789012345678901234567890'
               '12345678901234567890123456789012345678901234567890')  # 100
    result = plantagenet.Post.summarize(content)

    # then the summarized value is the same
    assert result == content

    # when a string has length > 100
    content2 = ('12345678901234567890123456789012345678901234567890'
                '123456789012345678901234567890123456789012345678901')  # 101
    expected2 = ('12345678901234567890123456789012345678901234567890'
                 '12345678901234567890123456789012345678901234567890...')
    result2 = plantagenet.Post.summarize(content2)

    # then the summarized value is truncated
    assert result2 == expected2


def test_summary_is_set_when_content_is_set():
    # given
    post = plantagenet.Post('title', 'content', datetime(2017, 1, 1))

    # when
    post.content = 'content2'

    # then
    assert post.summary == 'content2'


def test_content_is_not_None():
    # given
    post = plantagenet.Post('title', 'content', datetime(2017, 1, 1))

    # when
    post.content = None

    # then
    assert post.content == ''
    assert post.summary == ''


def test_get_by_slug():
    # given
    post1 = plantagenet.Post('title1', 'content1', datetime(2017, 1, 1))
    post2 = plantagenet.Post('title2', 'content2', datetime(2017, 1, 1))
    post3 = plantagenet.Post('title3', 'content3', datetime(2017, 1, 1))
    app.db.session.add(post1)
    app.db.session.add(post2)
    app.db.session.add(post3)

    # when
    result = plantagenet.Post.get_by_slug('title2')

    # then
    assert result is post2


def test_get_by_slug_missing():
    # given
    post1 = plantagenet.Post('title1', 'content1', datetime(2017, 1, 1))
    post2 = plantagenet.Post('title2', 'content2', datetime(2017, 1, 1))
    post3 = plantagenet.Post('title3', 'content3', datetime(2017, 1, 1))
    app.db.session.add(post1)
    app.db.session.add(post2)
    app.db.session.add(post3)

    # when
    result = plantagenet.Post.get_by_slug('title4')

    # then
    assert result is None


def test_get_unique_slug():
    # when
    slug = plantagenet.Post.get_unique_slug('title')

    # then
    assert slug == 'title'


def test_get_unique_slug_not_unique():
    # given a post that already exists
    post = plantagenet.Post('title', 'content', datetime(2017, 1, 1))
    app.db.session.add(post)

    # when we try to get a slug with the same value
    slug = plantagenet.Post.get_unique_slug('title')

    # then it increments a counter and returns the slightly different value
    assert slug == 'title-1'
