#!/usr/bin/env python3

from datetime import datetime

import pytest
from sqlalchemy.exc import OperationalError
from werkzeug.exceptions import NotFound

import plantagenet
from plantagenet import app


class TestPost:
    def setup_method(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        app.config['TESTING'] = True
        self.cl = app.test_client()
        app.testing = True
        self.ctx = app.app_context()
        self.ctx.push()
        app.db.create_all()

    def teardown_method(self):
        app.db.session.rollback()
        app.db.drop_all()
        self.ctx.pop()

    def test_init(self):
        # when a Post is created
        post = plantagenet.Post('title', 'content', datetime(2017, 1, 1))

        # then the title is the same as what was passed to the constructor
        assert post.title == 'title'

        # then the content is the same as what was passed to the constructor
        assert post.content == 'content'

        # then the date is the same as what was passed to the constructor
        assert post.date == datetime(2017, 1, 1)

    def test_init_optional_arg_is_draft(self):
        # when a Post is created
        post = plantagenet.Post('title', 'content', datetime(2017, 1, 1))

        # then optional argument "is_draft" have its default value of False
        assert not post.is_draft

    def test_init_set_is_draft(self):
        # when a Post is created
        post = plantagenet.Post('title', 'content', datetime(2017, 1, 1), True)

        # then the is_draft field is the same as what was passed to the
        # constructor
        assert post.is_draft

    def test_init_set_is_draft_named(self):
        # when a Post is created
        post = plantagenet.Post('title', 'content', datetime(2017, 1, 1),
                                is_draft=True)

        # then the is_draft field is the same as what was passed to the
        # constructor
        assert post.is_draft

    def test_init_optional_arg_notes(self):
        # when a Post is created
        post = plantagenet.Post('title', 'content', datetime(2017, 1, 1))

        # then optional argument "notes" have its default value of None
        assert post.notes is None

    def test_init_set_notes(self):
        # when a Post is created
        post = plantagenet.Post('title', 'content', datetime(2017, 1, 1),
                                False, 'notes')

        # then the notes field is the same as what was passed to the
        # constructor
        assert post.notes == 'notes'

    def test_init_set_notes_named(self):
        # when a Post is created
        post = plantagenet.Post('title', 'content', datetime(2017, 1, 1),
                                False, notes='notes')

        # then the notes field is the same as what was passed to the
        # constructor
        assert post.notes == 'notes'

    def test_init_set_slug_from_simple_title(self):
        # when a Post with a simple title is created
        post = plantagenet.Post('title', 'content', datetime(2017, 1, 1))

        # then the post's slug is set
        assert post.slug == 'title'

    def test_init_set_slug_from_title_with_spaces(self):
        # when a Post with a simple title is created
        post = plantagenet.Post('title  one', 'content', datetime(2017, 1, 1))

        # then the post's slug is set, with consecutive spaces replaced by a
        # single hyphen
        assert post.slug == 'title-one'

    def test_init_set_slug_from_title_with_leading_spaces(self):
        # when a Post with a simple title is created
        post = plantagenet.Post(' title', 'content', datetime(2017, 1, 1))

        # then the post's slug is set, with leading spaces removed
        assert post.slug == 'title'

    def test_init_set_slug_from_title_with_trailing_spaces(self):
        # when a Post with a simple title is created
        post = plantagenet.Post('title ', 'content', datetime(2017, 1, 1))

        # then the post's slug is set, with trailing spaces removed
        assert post.slug == 'title'

    def test_init_set_slug_from_title_with_non_word_characters(self):
        # when a Post with a simple title is created
        post = plantagenet.Post('title ! $,()', 'content',
                                datetime(2017, 1, 1))

        # then the post's slug is set, with non-word chars removed
        assert post.slug == 'title'

    def test_init_set_slug_from_title_with_upper_case(self):
        # when a Post with a simple title is created
        post = plantagenet.Post('TITLEtitletItLe', 'content',
                                datetime(2017, 1, 1))

        # then the post's slug is set
        assert post.slug == 'titletitletitle'

    def test_init_set_summary_from_content(self):
        # when a Post is created
        post = plantagenet.Post('title', 'content', datetime(2017, 1, 1))

        # then the post's summary is set from the content
        assert post.summary == 'content'

    def test_init_set_summary_from_content_truncated(self):
        # when a Post is created from content with length == 100
        content = '12345678901234567890123456789012345678901234567890' \
                  '12345678901234567890123456789012345678901234567890'  # 100
        post = plantagenet.Post('title', content, datetime(2017, 1, 1))

        # then the post's summary is set from the content without modification
        assert post.summary == content

        # when a Post is created from content with length > 100
        content2 = '12345678901234567890123456789012345678901234567890' \
                   '123456789012345678901234567890123456789012345678901'  # 101
        expected = '12345678901234567890123456789012345678901234567890' \
                   '12345678901234567890123456789012345678901234567890...'
        post = plantagenet.Post('title', content2, datetime(2017, 1, 1))

        # then the post's summary is set from the truncated content
        assert post.summary == expected

    def test_init_set_last_updated_date(self):
        post = plantagenet.Post('title', 'content', datetime(2017, 1, 1))

        # then the post's last_updated_date is set from the date
        assert post.last_updated_date == datetime(2017, 1, 1)

    def test_summarize_consecutive_spaces_are_condensed(self):
        # when
        result = plantagenet.Post.summarize('one  two')

        # then
        assert result == 'one two'

    def test_summarize_html_tags_are_removed(self):
        # when
        result = plantagenet.Post.summarize('<a href="/">Home</a>')

        # then
        assert result == 'Home'

    def test_summarize_punctuation_has_added_space(self):
        # when
        result = plantagenet.Post.summarize('one,two.three?four!five')

        # then
        assert result == 'one, two. three? four! five'

    def test_summarize_wordish_chars_are_kept(self):
        # when
        result = plantagenet.Post.summarize('Something,.?!')

        # then
        assert result == 'Something, . ? ! '

    def test_summarize_non_wordish_chars_are_removed(self):
        # when
        result = plantagenet.Post.summarize(
            'Something :@#$%^&*()[]-_=+[]{}\\|;:\'"/<>')

        # then
        assert result == 'Something '

    def test_summarize_long_values_are_truncated(self):
        # when a string has length == 100
        content = '12345678901234567890123456789012345678901234567890' \
                  '12345678901234567890123456789012345678901234567890'  # 100
        result = plantagenet.Post.summarize(content)

        # then the summarized value is the same
        assert result == content

        # when a string has length > 100
        content2 = '12345678901234567890123456789012345678901234567890' \
                   '123456789012345678901234567890123456789012345678901'  # 101
        expected2 = '12345678901234567890123456789012345678901234567890' \
                    '12345678901234567890123456789012345678901234567890...'
        result2 = plantagenet.Post.summarize(content2)

        # then the summarized value is truncated
        assert result2 == expected2

    def test_summary_is_set_when_content_is_set(self):
        # given
        post = plantagenet.Post('title', 'content', datetime(2017, 1, 1))

        # when
        post.content = 'content2'

        # then
        assert post.summary == 'content2'

    def test_content_is_not_None(self):
        # given
        post = plantagenet.Post('title', 'content', datetime(2017, 1, 1))

        # when
        post.content = None

        # then
        assert post.content == ''
        assert post.summary == ''

    def test_get_by_slug(self):
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

    def test_get_by_slug_missing(self):
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

    def test_get_unique_slug(self):
        # when
        slug = plantagenet.Post.get_unique_slug('title')

        # then
        assert slug == 'title'

    def test_get_unique_slug_not_unique(self):
        # given a post that already exists
        post = plantagenet.Post('title', 'content', datetime(2017, 1, 1))
        app.db.session.add(post)

        # when we try to get a slug with the same value
        slug = plantagenet.Post.get_unique_slug('title')

        # then it increments a counter and returns the slightly different value
        assert slug == 'title-1'


class TestCreateDb:
    def test_create_db_command(self):
        # given an app with uninitialize database
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        app.config['TESTING'] = True
        app.testing = True

        # precondition: the database tables have not been created yet
        with app.app_context():
            def query_post():
                plantagenet.db.session.execute(
                    plantagenet.db.select(plantagenet.Post)).first()

            def query_tag():
                plantagenet.db.session.execute(
                    plantagenet.db.select(plantagenet.Tag)).first()

            def query_option():
                plantagenet.db.session.execute(
                    plantagenet.db.select(plantagenet.Option)).first()

            with pytest.raises(OperationalError):
                query_post()
            plantagenet.db.session.rollback()
            with pytest.raises(OperationalError):
                query_tag()
            plantagenet.db.session.rollback()
            with pytest.raises(OperationalError):
                query_option()
            plantagenet.db.session.rollback()

        # when the create_db function is called
        plantagenet.cmd_create_db()

        # then the database tables are created
        with app.app_context():
            assert plantagenet.db.session.execute(
                plantagenet.db.select(plantagenet.Post)).first() is None
            assert plantagenet.db.session.execute(
                plantagenet.db.select(plantagenet.Tag)).first() is None
            assert plantagenet.db.session.execute(
                plantagenet.db.select(plantagenet.Option)).first() is None


class TestHashPassword:
    def test_hash_password(self):
        # given
        unhashed_password = '12345'

        # when
        result = plantagenet.hash_password(unhashed_password)

        # then
        assert plantagenet.bcrypt.check_password_hash(result,
                                                      unhashed_password)


class TestCliCommands:
    def setup_method(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        app.config['TESTING'] = True
        self.cl = app.test_client()
        app.testing = True
        self.ctx = app.app_context()
        self.ctx.push()
        app.db.create_all()

    def teardown_method(self):
        app.db.session.rollback()
        app.db.drop_all()
        self.ctx.pop()

    def test_reset_slug(self):
        # given a post with a non-standard slug is put into the db
        post = plantagenet.Post('title', 'content', datetime(2017, 1, 1))
        post.slug = 'slug12345'
        app.db.session.add(post)
        app.db.session.commit()

        # precondition: the post is in the db
        assert post.id is not None
        post2 = plantagenet.Post.query.first()
        assert post2.id is not None
        assert post2 is post

        # precondition: the post's slug is different from the title
        assert post.slug != 'title'

        # when the reset_slug function is called
        plantagenet.reset_slug(post.id)

        # then the post's slug is changed to match the title (plus
        # counter, meh)
        assert post.slug == post.title

    def test_reset_slug_missing(self):
        # precondition: no posts are in the db
        result = plantagenet.Post.query.first()
        assert result is None

        # when the function is called with the id of a nonexistent post,
        # then an exception is thrown
        with pytest.raises(NotFound):
            plantagenet.reset_slug(1)


class TestListTags:
    def setup_method(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        app.config['TESTING'] = True
        app.testing = True
        self.ctx = app.app_context()
        self.ctx.push()
        app.db.create_all()
        self.cl = app.test_client()

    def teardown_method(self):
        app.db.session.rollback()
        app.db.drop_all()
        self.ctx.pop()

    def test_list_tags_returns_200(self):
        # when
        response = self.cl.get('/tags')

        # then
        assert response.status_code == 200

    def test_list_tags_shows_tag_with_published_post(self):
        # given a tag with one published post
        tag = plantagenet.Tag('mytag')
        post = plantagenet.Post('title', 'content', datetime(2017, 1, 1))
        post.tags.append(tag)
        app.db.session.add(post)
        app.db.session.commit()

        # when an unauthenticated user visits /tags
        response = self.cl.get('/tags')

        # then the tag is visible
        assert b'mytag' in response.data

    def test_list_tags_hides_tag_with_only_draft_posts(self):
        # given a tag whose only post is a draft
        tag = plantagenet.Tag('drafttag')
        post = plantagenet.Post('title', 'content', datetime(2017, 1, 1),
                                is_draft=True)
        post.tags.append(tag)
        app.db.session.add(post)
        app.db.session.commit()

        # when an unauthenticated user visits /tags
        response = self.cl.get('/tags')

        # then the tag is not visible
        assert b'drafttag' not in response.data

    def test_list_tags_authenticated_shows_tag_with_only_draft_posts(self):
        # given a tag whose only post is a draft
        tag = plantagenet.Tag('drafttag')
        post = plantagenet.Post('title', 'content', datetime(2017, 1, 1),
                                is_draft=True)
        post.tags.append(tag)
        app.db.session.add(post)
        app.db.session.commit()

        # when an authenticated user visits /tags
        with self.cl.session_transaction() as sess:
            sess['_user_id'] = 'admin'
            sess['_fresh'] = True
        response = self.cl.get('/tags')

        # then the tag is visible
        assert b'drafttag' in response.data


class TestListPages:
    def setup_method(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        app.config['TESTING'] = True
        app.testing = True
        self.ctx = app.app_context()
        self.ctx.push()
        app.db.create_all()
        self.cl = app.test_client()

    def teardown_method(self):
        app.db.session.rollback()
        app.db.drop_all()
        self.ctx.pop()

    def test_list_pages_returns_200(self):
        response = self.cl.get('/page')
        assert response.status_code == 200

    def test_list_pages_shows_published_page(self):
        page = plantagenet.Page('My Page', 'content', datetime(2024, 1, 1))
        app.db.session.add(page)
        app.db.session.commit()

        response = self.cl.get('/page')
        assert b'My Page' in response.data

    def test_list_pages_hides_draft_from_unauthenticated(self):
        page = plantagenet.Page('Secret Page', 'content', datetime(2024, 1, 1),
                                is_draft=True)
        app.db.session.add(page)
        app.db.session.commit()

        response = self.cl.get('/page')
        assert b'Secret Page' not in response.data

    def test_list_pages_shows_draft_to_authenticated(self):
        page = plantagenet.Page('Secret Page', 'content', datetime(2024, 1, 1),
                                is_draft=True)
        app.db.session.add(page)
        app.db.session.commit()

        with self.cl.session_transaction() as sess:
            sess['_user_id'] = 'admin'
            sess['_fresh'] = True
        response = self.cl.get('/page')
        assert b'Secret Page' in response.data


class TestViewPage:
    def setup_method(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        app.config['TESTING'] = True
        app.testing = True
        self.ctx = app.app_context()
        self.ctx.push()
        app.db.create_all()
        self.cl = app.test_client()

    def teardown_method(self):
        app.db.session.rollback()
        app.db.drop_all()
        self.ctx.pop()

    def test_view_page_returns_200(self):
        page = plantagenet.Page('My Page', 'content', datetime(2024, 1, 1))
        app.db.session.add(page)
        app.db.session.commit()

        response = self.cl.get('/page/{}'.format(page.slug))
        assert response.status_code == 200

    def test_view_page_shows_content(self):
        page = plantagenet.Page('My Page', 'Hello World', datetime(2024, 1, 1))
        app.db.session.add(page)
        app.db.session.commit()

        response = self.cl.get('/page/{}'.format(page.slug))
        assert b'Hello World' in response.data

    def test_view_page_missing_returns_404(self):
        response = self.cl.get('/page/no-such-page')
        assert response.status_code == 404

    def test_view_draft_page_unauthenticated_returns_401(self):
        page = plantagenet.Page('Draft', 'content', datetime(2024, 1, 1),
                                is_draft=True)
        app.db.session.add(page)
        app.db.session.commit()

        response = self.cl.get('/page/{}'.format(page.slug))
        assert response.status_code == 401

    def test_view_draft_page_authenticated_returns_200(self):
        page = plantagenet.Page('Draft', 'content', datetime(2024, 1, 1),
                                is_draft=True)
        app.db.session.add(page)
        app.db.session.commit()

        with self.cl.session_transaction() as sess:
            sess['_user_id'] = 'admin'
            sess['_fresh'] = True
        response = self.cl.get('/page/{}'.format(page.slug))
        assert response.status_code == 200


class TestPagePublishedDate:
    def setup_method(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        app.config['TESTING'] = True
        app.testing = True
        self.ctx = app.app_context()
        self.ctx.push()
        app.db.create_all()
        self.cl = app.test_client()

    def teardown_method(self):
        app.db.session.rollback()
        app.db.drop_all()
        self.ctx.pop()

    def _login(self):
        with self.cl.session_transaction() as sess:
            sess['_user_id'] = 'admin'
            sess['_fresh'] = True

    def test_published_date_none_for_draft(self):
        page = plantagenet.Page('My Page', 'content', datetime(2024, 1, 1),
                                is_draft=True)
        assert page.published_date is None

    def test_published_date_set_on_create_when_not_draft(self):
        self._login()
        self.cl.post('/new-page', data={
            'title': 'My Page',
            'content': 'content',
            'notes': '',
        })
        page = app.db.session.execute(
            plantagenet.db.select(plantagenet.Page)).scalar()
        assert page.published_date is not None

    def test_published_date_not_set_on_create_when_draft(self):
        self._login()
        self.cl.post('/new-page', data={
            'title': 'My Page',
            'content': 'content',
            'notes': '',
            'is_draft': 'on',
        })
        page = app.db.session.execute(
            plantagenet.db.select(plantagenet.Page)).scalar()
        assert page.published_date is None

    def test_published_date_set_when_draft_is_published(self):
        page = plantagenet.Page('My Page', 'content', datetime(2024, 1, 1),
                                is_draft=True)
        app.db.session.add(page)
        app.db.session.commit()
        assert page.published_date is None

        self._login()
        self.cl.post('/page/{}/edit'.format(page.slug), data={
            'title': page.title,
            'content': page.content,
            'notes': '',
        })
        app.db.session.refresh(page)
        assert page.published_date is not None

    def test_published_date_not_overwritten_on_re_save(self):
        original_date = datetime(2020, 6, 15)
        page = plantagenet.Page('My Page', 'content', datetime(2024, 1, 1))
        page.published_date = original_date
        app.db.session.add(page)
        app.db.session.commit()

        self._login()
        self.cl.post('/page/{}/edit'.format(page.slug), data={
            'title': page.title,
            'content': 'updated content',
            'notes': '',
        })
        app.db.session.refresh(page)
        assert page.published_date == original_date


class TestVersion:
    def test_version_number_is_correct(self):
        from plantagenet import Options
        # expect
        assert Options.get_version() == 'unknown'
