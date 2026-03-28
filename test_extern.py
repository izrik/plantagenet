import os
import tempfile

import jinja2
import pytest

from plantagenet import app, Config, Options


@pytest.fixture(autouse=True)
def db_setup():
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
    app.config['TESTING'] = True
    app.testing = True
    with app.app_context():
        app.db.create_all()
        yield
        app.db.session.rollback()


class TestGetExtraLinks:
    def setup_method(self):
        self._original = Config.EXTRA_LINKS

    def teardown_method(self):
        Config.EXTRA_LINKS = self._original

    def test_empty_string_returns_empty_list(self):
        Config.EXTRA_LINKS = ''
        assert Options.get_extra_links() == []

    def test_single_link(self):
        Config.EXTRA_LINKS = 'About:/pages/about.html'
        assert Options.get_extra_links() == [('About', '/pages/about.html')]

    def test_multiple_links(self):
        Config.EXTRA_LINKS = 'About:/pages/about.html,Resume:/pages/resume.pdf'
        assert Options.get_extra_links() == [
            ('About', '/pages/about.html'),
            ('Resume', '/pages/resume.pdf'),
        ]

    def test_url_containing_colon(self):
        Config.EXTRA_LINKS = 'Home:http://example.com'
        assert Options.get_extra_links() == [('Home', 'http://example.com')]

    def test_item_without_colon_is_skipped(self):
        Config.EXTRA_LINKS = (
            'About:/pages/about.html,baditem,Resume:/pages/resume.pdf')
        assert Options.get_extra_links() == [
            ('About', '/pages/about.html'),
            ('Resume', '/pages/resume.pdf'),
        ]

    def test_whitespace_is_stripped(self):
        Config.EXTRA_LINKS = ' About : /pages/about.html '
        assert Options.get_extra_links() == [('About', '/pages/about.html')]


class TestGetPage:
    def setup_method(self):
        self._original_extern_root = Config.EXTERN_ROOT
        self._original_jinja_loader = app.jinja_loader

    def teardown_method(self):
        Config.EXTERN_ROOT = self._original_extern_root
        app.jinja_loader = self._original_jinja_loader

    def test_no_extern_root_returns_404(self):
        Config.EXTERN_ROOT = None
        with app.test_client() as client:
            response = client.get('/pages/about.html')
        assert response.status_code == 404

    def test_html_file_is_rendered_as_template(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            os.makedirs(os.path.join(tmpdir, 'pages'))
            with open(os.path.join(tmpdir, 'pages', 'about.html'), 'w') as f:
                f.write('<p>About page content</p>')

            Config.EXTERN_ROOT = tmpdir
            app.jinja_loader = jinja2.ChoiceLoader([
                jinja2.FileSystemLoader(tmpdir),
                self._original_jinja_loader,
            ])

            with app.test_client() as client:
                response = client.get('/pages/about.html')
        assert response.status_code == 200
        assert b'About page content' in response.data

    def test_non_html_file_is_served_directly(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            os.makedirs(os.path.join(tmpdir, 'pages'))
            with open(os.path.join(tmpdir, 'pages', 'file.txt'), 'w') as f:
                f.write('hello world')

            Config.EXTERN_ROOT = tmpdir

            with app.test_client() as client:
                response = client.get('/pages/file.txt')
        assert response.status_code == 200
        assert b'hello world' in response.data

    def test_missing_file_returns_404(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            os.makedirs(os.path.join(tmpdir, 'pages'))
            Config.EXTERN_ROOT = tmpdir
            app.jinja_loader = jinja2.ChoiceLoader([
                jinja2.FileSystemLoader(tmpdir),
                self._original_jinja_loader,
            ])

            with app.test_client() as client:
                response = client.get('/pages/nonexistent.html')
        assert response.status_code == 404

    def test_missing_binary_file_returns_404(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            os.makedirs(os.path.join(tmpdir, 'pages'))
            Config.EXTERN_ROOT = tmpdir

            with app.test_client() as client:
                response = client.get('/pages/nonexistent.pdf')
        assert response.status_code == 404
