import jinja2
import pytest

from plantagenet import app, Config, Option, Options


@pytest.fixture(autouse=True)
def db_setup():
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
    app.config['TESTING'] = True
    app.testing = True
    with app.app_context():
        app.db.create_all()
        yield
        app.db.session.rollback()


def test_extra_links_empty_string_returns_empty_list(monkeypatch):
    monkeypatch.setattr(Config, 'EXTRA_LINKS', '')
    assert Options.get_extra_links() == []


def test_extra_links_single_link(monkeypatch):
    monkeypatch.setattr(Config, 'EXTRA_LINKS', 'About:/pages/about.html')
    assert Options.get_extra_links() == [('About', '/pages/about.html')]


def test_extra_links_multiple_links(monkeypatch):
    monkeypatch.setattr(Config, 'EXTRA_LINKS',
                        'About:/pages/about.html,Resume:/pages/resume.pdf')
    assert Options.get_extra_links() == [
        ('About', '/pages/about.html'),
        ('Resume', '/pages/resume.pdf'),
    ]


def test_extra_links_url_containing_colon(monkeypatch):
    monkeypatch.setattr(Config, 'EXTRA_LINKS', 'Home:http://example.com')
    assert Options.get_extra_links() == [('Home', 'http://example.com')]


def test_extra_links_item_without_colon_is_skipped(monkeypatch):
    monkeypatch.setattr(Config, 'EXTRA_LINKS',
                        'About:/pages/about.html,baditem,'
                        'Resume:/pages/resume.pdf')
    assert Options.get_extra_links() == [
        ('About', '/pages/about.html'),
        ('Resume', '/pages/resume.pdf'),
    ]


def test_extra_links_whitespace_is_stripped(monkeypatch):
    monkeypatch.setattr(Config, 'EXTRA_LINKS', ' About : /pages/about.html ')
    assert Options.get_extra_links() == [('About', '/pages/about.html')]


def test_extra_links_db_option_takes_precedence_over_envvar(monkeypatch):
    monkeypatch.setattr(Config, 'EXTRA_LINKS', 'Envvar:/envvar')
    with app.app_context():
        app.db.session.add(Option('extra_links', 'DB:/db'))
        assert Options.get_extra_links() == [('DB', '/db')]


def test_extra_links_falls_back_to_envvar_when_db_option_absent(monkeypatch):
    monkeypatch.setattr(Config, 'EXTRA_LINKS', 'Envvar:/envvar')
    with app.app_context():
        assert Options.get_extra_links() == [('Envvar', '/envvar')]


def test_get_page_no_extern_root_returns_404(monkeypatch):
    monkeypatch.setattr(Config, 'EXTERN_ROOT', None)
    with app.test_client() as client:
        response = client.get('/pages/about.html')
    assert response.status_code == 404


def test_get_page_html_file_is_rendered_as_template(monkeypatch, tmp_path):
    pages_dir = tmp_path / 'pages'
    pages_dir.mkdir()
    (pages_dir / 'about.html').write_text('<p>About page content</p>')

    monkeypatch.setattr(Config, 'EXTERN_ROOT', str(tmp_path))
    original_loader = app.jinja_loader
    monkeypatch.setattr(app, 'jinja_loader', jinja2.ChoiceLoader([
        jinja2.FileSystemLoader(str(tmp_path)),
        original_loader,
    ]))

    with app.test_client() as client:
        response = client.get('/pages/about.html')
    assert response.status_code == 200
    assert b'About page content' in response.data


def test_get_page_non_html_file_is_served_directly(monkeypatch, tmp_path):
    pages_dir = tmp_path / 'pages'
    pages_dir.mkdir()
    (pages_dir / 'file.txt').write_text('hello world')

    monkeypatch.setattr(Config, 'EXTERN_ROOT', str(tmp_path))

    with app.test_client() as client:
        response = client.get('/pages/file.txt')
    assert response.status_code == 200
    assert b'hello world' in response.data


def test_get_page_missing_file_returns_404(monkeypatch, tmp_path):
    pages_dir = tmp_path / 'pages'
    pages_dir.mkdir()

    monkeypatch.setattr(Config, 'EXTERN_ROOT', str(tmp_path))
    original_loader = app.jinja_loader
    monkeypatch.setattr(app, 'jinja_loader', jinja2.ChoiceLoader([
        jinja2.FileSystemLoader(str(tmp_path)),
        original_loader,
    ]))

    with app.test_client() as client:
        response = client.get('/pages/nonexistent.html')
    assert response.status_code == 404


def test_get_page_missing_binary_file_returns_404(monkeypatch, tmp_path):
    pages_dir = tmp_path / 'pages'
    pages_dir.mkdir()

    monkeypatch.setattr(Config, 'EXTERN_ROOT', str(tmp_path))

    with app.test_client() as client:
        response = client.get('/pages/nonexistent.pdf')
    assert response.status_code == 404
