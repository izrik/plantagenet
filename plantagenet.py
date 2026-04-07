#!/usr/bin/env python3

# plantagenet - a python blogging system
# Copyright (C) 2016-2017 izrik
#
# This file is a part of plantagenet.
#
# Plantagenet is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Plantagenet is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with plantagenet.  If not, see <http://www.gnu.org/licenses/>.


import argparse
from datetime import datetime
from itertools import cycle
import os
from os import environ
import re
import secrets

import dateutil.parser
from flask import flash
from flask import Flask
from markupsafe import Markup
from flask import redirect
from flask import render_template
from flask import request
from flask import send_from_directory
from flask import url_for
from flask_bcrypt import Bcrypt
from flask_login import AnonymousUserMixin
from flask_login import current_user
from flask_login import login_required
from flask_login import login_user
from flask_login import LoginManager
from flask_login import logout_user
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import git
import jinja2
from slugify import slugify
from werkzeug.exceptions import BadRequest
from werkzeug.exceptions import NotFound
from werkzeug.exceptions import ServiceUnavailable
from werkzeug.exceptions import Unauthorized

try:
    from __version__ import __version__
except ImportError:
    __version__ = 'unknown'

try:
    _repo = git.Repo('.')
    __revision__ = _repo.head.commit.hexsha
    if _repo.is_dirty():
        __revision__ += '-dirty'
except git.InvalidGitRepositoryError:
    __revision__ = environ.get('PLANTAGENET_REVISION', 'unknown')


class PlantagenetError(Exception):
    pass


class ConfigError(PlantagenetError):
    pass


class Config(object):
    SECRET_KEY = environ.get('PLANTAGENET_SECRET_KEY', 'secret')
    HOST = environ.get('PLANTAGENET_HOST', '127.0.0.1')
    PORT = environ.get('PLANTAGENET_PORT', 1177)
    DEBUG = environ.get('PLANTAGENET_DEBUG', False)
    DB_URI = environ.get('PLANTAGENET_DB_URI')
    DB_URI_FILE = environ.get('PLANTAGENET_DB_URI_FILE')
    SITENAME = environ.get('PLANTAGENET_SITENAME', 'Site Name')
    SITEURL = environ.get('PLANTAGENET_SITEURL', 'http://localhost:1177')
    CUSTOM_TEMPLATES = environ.get('PLANTAGENET_CUSTOM_TEMPLATES', None)
    AUTHOR = environ.get('PLANTAGENET_AUTHOR', 'The Author')
    LOCAL_RESOURCES = environ.get('PLANTAGENET_LOCAL_RESOURCES', False)
    EXTERN_ROOT = environ.get('PLANTAGENET_EXTERN_ROOT', None)
    EXTRA_LINKS = environ.get('PLANTAGENET_EXTRA_LINKS', '')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--secret-key', type=str,
                        default=Config.SECRET_KEY, help='')
    parser.add_argument('--host', type=str, default=Config.HOST,
                        help='The ip address to listen on. Set to 0.0.0.0 to '
                             'accept any incoming connections on any network '
                             'interface. Defaults to 127.0.0.1 for testing.')
    parser.add_argument('--port', type=int, default=Config.PORT,
                        help='')
    parser.add_argument('--debug', action='store_true', help='',
                        default=Config.DEBUG)
    parser.add_argument('--db-uri', type=str, action='store',
                        default=Config.DB_URI)
    parser.add_argument('--db-uri-file', action='store',
                        default=Config.DB_URI_FILE)
    parser.add_argument('--sitename', type=str,
                        default=Config.SITENAME, help='')
    parser.add_argument('--siteurl', type=str,
                        default=Config.SITEURL, help='')
    parser.add_argument('--custom-templates', type=str,
                        default=Config.CUSTOM_TEMPLATES,
                        help="The path to a directory on the filesystem from "
                             "which to load template files. If none is "
                             "specified, the app's default internal template "
                             "location will be used.")
    parser.add_argument('--author', type=str, default=Config.AUTHOR,
                        help='The name of the author of the site. This name '
                             'will appear in the "Posted by" line on posts, '
                             'and in the copyright section in the footer.')
    parser.add_argument('--local-resources', action='store_true',
                        default=Config.LOCAL_RESOURCES,
                        help='Use local resources (CSS and JS served from the '
                             'app instead of from global URLs).')
    parser.add_argument('--extern-root', type=str,
                        default=Config.EXTERN_ROOT,
                        help='Path to a directory containing external pages '
                             '(under pages/) and other static files to serve '
                             'under /pages/.')
    parser.add_argument('--extra-links', type=str,
                        default=Config.EXTRA_LINKS,
                        help='Comma-separated list of Label:URL pairs to add '
                             'to the navbar, e.g. "About:/pages/about.html,'
                             'Resume:/pages/resume.pdf".')

    parser.add_argument('--create-secret-key', action='store_true')
    parser.add_argument('--create-db', action='store_true')
    parser.add_argument('--hash-password', action='store', metavar='PASSWORD')
    parser.add_argument('--count-posts', action='store_true')
    parser.add_argument('--reset-slug', action='store', metavar='POST_ID')
    parser.add_argument('--set-date', action='store', nargs=2,
                        metavar=('POST_ID', 'DATE'))
    parser.add_argument('--set-last-updated-date', action='store', nargs=2,
                        metavar=('POST_ID', 'DATE'))
    parser.add_argument('--reset-summary', action='store', metavar='POST_ID')
    parser.add_argument('--set-option', action='store', nargs=2,
                        metavar=('NAME', 'VALUE'))
    parser.add_argument('--clear-option', action='store', metavar='NAME')

    args = parser.parse_args()

    if args.create_secret_key:
        digits = '0123456789abcdef'
        key = ''.join((secrets.choice(digits) for x in range(48)))
        print(key)
        exit(0)

    Config.SECRET_KEY = args.secret_key
    Config.HOST = args.host
    Config.PORT = args.port
    Config.DEBUG = args.debug
    Config.DB_URI = args.db_uri
    Config.DB_URI_FILE = args.db_uri_file
    Config.SITENAME = args.sitename
    Config.SITEURL = args.siteurl
    Config.CUSTOM_TEMPLATES = args.custom_templates
    Config.AUTHOR = args.author
    Config.LOCAL_RESOURCES = args.local_resources
    Config.EXTERN_ROOT = args.extern_root
    Config.EXTRA_LINKS = args.extra_links


# extensions (unbound; initialized per-app in create_app)
login_manager = LoginManager()
db = SQLAlchemy()
bcrypt = Bcrypt()


# user class for providing authentication
class User(UserMixin):
    def __init__(self, name, email):
        self.id = name
        self.name = name
        self.email = email

    def get_name(self):
        return self.name

    @property
    def is_authenticated(self):
        return True


class Guest(AnonymousUserMixin):
    pass


tags_table = db.Table(
    'tags_posts',
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), index=True),
    db.Column('post_id', db.Integer, db.ForeignKey('post.id'), index=True))


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    _title = db.Column(db.String(100), name='title')
    slug = db.Column(db.String(100), index=True, unique=True)
    _content = db.Column(db.Text, name='content')
    summary = db.Column(db.Text)
    notes = db.Column(db.Text)
    date = db.Column(db.DateTime)
    last_updated_date = db.Column(db.DateTime, nullable=False)
    is_draft = db.Column(db.Boolean, nullable=False, default=False)
    tags = db.relationship('Tag', secondary=tags_table,
                           backref=db.backref('posts'))

    def __init__(self, title, content, date, is_draft=False, notes=None):
        self.title = title
        self.content = content
        self.date = date
        self.last_updated_date = date
        self.is_draft = is_draft
        self.notes = notes

    @property
    def content(self):
        return self._content

    @staticmethod
    def summarize(value):
        stripped = re.sub(r'</?[^>]+/?>', '', value)
        cleaned = re.sub(r'[^a-zA-Z01-9,.?!]', ' ', stripped)
        normalized = re.sub(r'\s*([.,?!])\s*', r'\1 ', cleaned)
        condensed = re.sub(r'\s+', ' ', normalized)
        truncated = condensed
        if len(truncated) > 100:
            truncated = condensed[:100] + '...'
        return truncated

    @content.setter
    def content(self, value):
        if value is None:
            value = ''
        value = str(value)
        self._content = value
        self.summary = self.summarize(value)

    @classmethod
    def get_by_slug(cls, slug):
        return db.session.execute(
            db.select(Post).filter_by(slug=slug)).scalar()

    @classmethod
    def get_unique_slug(cls, title):
        slug = slugify(title)

        def slug_count(s):
            return db.session.execute(
                db.select(db.func.count(Post.id)).where(
                    Post.slug == s)).scalar()

        if slug_count(slug) > 0:
            i = 1
            while slug_count(slug) > 0:
                slug = slugify('{} {}'.format(title, i))
                i += 1
        return slug

    @staticmethod
    def validate_title(title):
        if not title or not slugify(title).strip():
            raise BadRequest("The post's title is invalid.")

    @staticmethod
    def tags_from_string(tag_string):
        tag_names = set(
            name for name in (
                name.strip() for name in tag_string.split(',') if name)
            if name)
        tags = set()
        for name in tag_names:
            tag = db.session.execute(
                db.select(Tag).filter_by(name=name)).scalar()
            if tag is None:
                tag = Tag(name)
            tags.add(tag)
        return tags

    def get_next(self, include_drafts=True):
        stmt = db.select(Post).where(Post.date > self.date)
        if not include_drafts:
            stmt = stmt.filter_by(is_draft=False)
        return db.session.execute(
            stmt.order_by(Post.date.asc()).limit(1)).scalar()

    def get_prev(self, include_drafts=True):
        stmt = db.select(Post).where(Post.date < self.date)
        if not include_drafts:
            stmt = stmt.filter_by(is_draft=False)
        return db.session.execute(
            stmt.order_by(Post.date.desc()).limit(1)).scalar()

    @classmethod
    def list_paginated(cls, include_drafts=False):
        stmt = db.select(Post)
        if not include_drafts:
            stmt = stmt.filter_by(is_draft=False)
        stmt = stmt.order_by(Post.date.desc())
        return db.paginate(stmt)

    def save(self):
        for tag in self.tags:
            db.session.add(tag)
        db.session.add(self)
        db.session.commit()

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        self._title = value
        if not self.slug and self._title:
            self.slug = self.get_unique_slug(self._title)


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)

    def __init__(self, name):
        self.name = name

    @classmethod
    def list(cls):
        return db.session.execute(db.select(Tag)).scalars()

    @classmethod
    def get(cls, tag_id):
        return db.session.get(Tag, tag_id)

    def post_count(self, include_drafts=False):
        stmt = (db.select(db.func.count()).select_from(Post)
                .join(Post.tags).where(Tag.id == self.id))
        if not include_drafts:
            stmt = stmt.where(Post.is_draft == False)  # noqa: E712
        return db.session.execute(stmt).scalar()

    def get_posts(self, include_drafts=False):
        stmt = db.select(Post).join(Post.tags).where(Tag.id == self.id)
        if not include_drafts:
            stmt = stmt.where(Post.is_draft == False)  # noqa: E712
        return db.session.execute(stmt).scalars()


class Page(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    _title = db.Column(db.String(100), name='title')
    slug = db.Column(db.String(100), index=True, unique=True)
    _content = db.Column(db.Text, name='content')
    notes = db.Column(db.Text)
    date = db.Column(db.DateTime)
    last_updated_date = db.Column(db.DateTime, nullable=False)
    published_date = db.Column(db.DateTime, nullable=True)
    is_draft = db.Column(db.Boolean, nullable=False, default=False)

    def __init__(self, title, content, date, is_draft=False, notes=None):
        self.title = title
        self.content = content
        self.date = date
        self.last_updated_date = date
        self.is_draft = is_draft
        self.notes = notes

    @property
    def content(self):
        return self._content

    @content.setter
    def content(self, value):
        if value is None:
            value = ''
        self._content = str(value)

    @classmethod
    def get_by_slug(cls, slug):
        return db.session.execute(
            db.select(Page).filter_by(slug=slug)).scalar()

    @classmethod
    def get_unique_slug(cls, title):
        slug = slugify(title)

        def slug_count(s):
            return db.session.execute(
                db.select(db.func.count(Page.id)).where(
                    Page.slug == s)).scalar()

        if slug_count(slug) > 0:
            i = 1
            while slug_count(slug) > 0:
                slug = slugify('{} {}'.format(title, i))
                i += 1
        return slug

    @staticmethod
    def validate_title(title):
        if not title or not slugify(title).strip():
            raise BadRequest("The page's title is invalid.")

    @classmethod
    def list(cls, include_drafts=False):
        stmt = db.select(Page)
        if not include_drafts:
            stmt = stmt.filter_by(is_draft=False)
        stmt = stmt.order_by(Page._title.asc())
        return db.session.execute(stmt).scalars()

    def save(self):
        db.session.add(self)
        db.session.commit()

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        self._title = value
        if not self.slug and self._title:
            self.slug = self.get_unique_slug(self._title)


class Option(db.Model):
    name = db.Column(db.String(100), primary_key=True)
    value = db.Column(db.String(100), nullable=True)

    def __init__(self, name, value):
        self.name = name
        self.value = value


class Options(object):
    @staticmethod
    def get(key, default_value=None):
        option = db.session.get(Option, key)
        if option is None:
            return default_value
        return option.value

    @staticmethod
    def set(key, value):
        option = db.session.get(Option, key)
        if option:
            option.value = value
        else:
            option = Option(key, value)
        db.session.add(option)
        db.session.commit()

    @staticmethod
    def get_sitename():
        return Options.get('sitename', Config.SITENAME)

    @staticmethod
    def get_siteurl():
        return Options.get('siteurl', Config.SITEURL)

    @staticmethod
    def get_revision():
        return __revision__

    @staticmethod
    def get_version():
        return __version__

    @staticmethod
    def seq():
        i = 0
        while True:
            yield i
            i += 1

    cycle = cycle

    @staticmethod
    def get_author():
        return Options.get('author', Config.AUTHOR)

    @staticmethod
    def should_use_local_resources():
        return Config.LOCAL_RESOURCES

    @staticmethod
    def get_extra_links():
        raw = Options.get('extra_links', Config.EXTRA_LINKS)
        links = []
        for item in raw.split(','):
            item = item.strip()
            if ':' in item:
                label, url = item.split(':', 1)
                links.append((label.strip(), url.strip()))
        return links


@login_manager.user_loader
def load_user(user_id):
    return User(Options.get_author(), Options.get_author())


def setup_options():
    return {'Options': Options}


def render_gfm(s):
    import pycmarkgfm
    from pycmarkgfm import options as cmark_options
    output = pycmarkgfm.gfm_to_html(s, options=cmark_options.hardbreaks)
    return Markup(output)  # nosec B704 - trusted author content


def index():
    pager = Post.list_paginated(include_drafts=current_user.is_authenticated)
    return render_template("index.html", pager=pager)


def login():
    if request.method == 'GET':
        return render_template('login.html')

    stored_password = Options.get('hashed_password')
    if not stored_password:
        raise ServiceUnavailable('No password set')
    password = request.form['password']
    if not bcrypt.check_password_hash(stored_password, password):
        flash('Password is invalid', 'error')
        return redirect(url_for('login'))

    user = User(Options.get_author(), Options.get_author())
    login_user(user)
    flash('Logged in successfully')
    # return redirect(request.args.get('next_url') or url_for('index'))
    return redirect(url_for('index'))


def get_post(slug):

    post = Post.get_by_slug(slug)
    if not post:
        raise NotFound()
    if post.is_draft and not current_user.is_authenticated:
        raise Unauthorized()
    user = current_user

    include_drafts = current_user.is_authenticated
    next_post = post.get_next(include_drafts=include_drafts)
    prev_post = post.get_prev(include_drafts=include_drafts)

    return render_template('post.html', config=Config, post=post, user=user,
                           next_post=next_post, prev_post=prev_post)


@login_required
def edit_post(slug):
    post = Post.get_by_slug(slug)
    if not post:
        raise NotFound()
    if request.method == 'GET':
        return render_template('edit.html', post=post, config=Config,
                               post_url=url_for('edit_post', slug=post.slug))

    title = request.form['title'].strip()
    Post.validate_title(title)
    content = request.form['content']
    notes = request.form['notes']
    is_draft = not (not ('is_draft' in request.form and
                         request.form['is_draft']))
    tags = request.form['tags']

    post.title = title
    post.content = content
    post.notes = notes
    post.is_draft = is_draft
    post.last_updated_date = datetime.now()

    current_tags = set(post.tags)
    next_tags = Post.tags_from_string(tags)
    tags_to_add = next_tags.difference(current_tags)
    tags_to_remove = current_tags.difference(next_tags)

    for ttr in tags_to_remove:
        post.tags.remove(ttr)
    post.tags.extend(tags_to_add)

    post.save()
    return redirect(url_for('get_post', slug=post.slug))


@login_required
def create_new():
    if request.method == 'GET':
        post = Post('', '', datetime.now(), True)
        return render_template('edit.html', post=post, config=Config,
                               post_url=url_for('create_new'))

    title = request.form['title'].strip()
    Post.validate_title(title)
    content = request.form['content']
    notes = request.form['notes']
    is_draft = not (not ('is_draft' in request.form and
                         request.form['is_draft']))
    tags = request.form['tags']

    post = Post(title, content, datetime.now(), is_draft, notes)
    post.tags.extend(Post.tags_from_string(tags))

    post.save()
    return redirect(url_for('get_post', slug=post.slug))


def list_tags():
    tags = Tag.list()
    include_drafts = current_user.is_authenticated
    tag_counts = [(tag, tag.post_count(include_drafts=include_drafts))
                  for tag in tags]
    return render_template('list_tags.html', tag_counts=tag_counts)


def get_tag(tag_id):
    tag = Tag.get(tag_id)
    posts = tag.get_posts(include_drafts=current_user.is_authenticated)
    return render_template("tag.html", tag=tag, posts=posts)


def list_pages():
    pages = Page.list(include_drafts=current_user.is_authenticated)
    return render_template('list_pages.html', pages=pages)


def view_page(slug):
    page = Page.get_by_slug(slug)
    if not page:
        raise NotFound()
    if page.is_draft and not current_user.is_authenticated:
        raise Unauthorized()
    return render_template('page.html', page=page)


@login_required
def edit_page(slug):
    page = Page.get_by_slug(slug)
    if not page:
        raise NotFound()
    if request.method == 'GET':
        return render_template('edit_page.html', page=page,
                               page_url=url_for('edit_page', slug=page.slug))

    title = request.form['title'].strip()
    Page.validate_title(title)
    content = request.form['content']
    notes = request.form['notes']
    is_draft = not (not ('is_draft' in request.form and
                         request.form['is_draft']))

    page.title = title
    page.content = content
    page.notes = notes
    page.last_updated_date = datetime.now()
    if not is_draft and page.published_date is None:
        page.published_date = datetime.now()
    page.is_draft = is_draft

    page.save()
    return redirect(url_for('view_page', slug=page.slug))


@login_required
def create_new_page():
    if request.method == 'GET':
        page = Page('', '', datetime.now(), True)
        return render_template('edit_page.html', page=page,
                               page_url=url_for('create_new_page'))

    title = request.form['title'].strip()
    Page.validate_title(title)
    content = request.form['content']
    notes = request.form['notes']
    is_draft = not (not ('is_draft' in request.form and
                         request.form['is_draft']))

    page = Page(title, content, datetime.now(), is_draft, notes)
    if not is_draft:
        page.published_date = page.date

    page.save()
    return redirect(url_for('view_page', slug=page.slug))


def logout():
    logout_user()
    return redirect("/")


@login_required
def admin():
    if request.method == 'GET':
        return render_template('admin.html',
                               sitename=Options.get_sitename(),
                               extra_links=Options.get('extra_links', ''))

    sitename = request.form.get('sitename', '').strip()
    if sitename:
        Options.set('sitename', sitename)

    new_password = request.form.get('new_password', '').strip()
    if new_password:
        hashed = bcrypt.generate_password_hash(new_password).decode('utf-8')
        Options.set('hashed_password', hashed)

    extra_links = request.form.get('extra_links', '').strip()
    Options.set('extra_links', extra_links)

    flash('Settings saved.')
    return redirect(url_for('admin'))


def get_page(filename):
    if not Config.EXTERN_ROOT:
        raise NotFound()
    if filename.endswith('.html'):
        try:
            return render_template('pages/' + filename)
        except jinja2.TemplateNotFound:
            raise NotFound()
    pages_dir = os.path.join(Config.EXTERN_ROOT, 'pages')
    return send_from_directory(pages_dir, filename)


def run_migrations(engine):
    migrations_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 'migrations')
    if not os.path.isdir(migrations_dir):
        return

    migration_re = re.compile(r'^v(\d+)\.(\d+)(?:\.(\d+))?\.sql$')
    files = []
    for fname in os.listdir(migrations_dir):
        m = migration_re.match(fname)
        if m:
            major = int(m.group(1))
            minor = int(m.group(2))
            patch = int(m.group(3)) if m.group(3) is not None else 0
            version_str = fname[1:-4]  # strip leading 'v' and trailing '.sql'
            files.append(((major, minor, patch), version_str, fname))

    files.sort(key=lambda x: x[0])

    with engine.connect() as conn:
        conn.execute(text(
            'CREATE TABLE IF NOT EXISTS schema_migrations '
            '(version TEXT PRIMARY KEY, '
            "applied_at TEXT NOT NULL DEFAULT (datetime('now')))"
        ))
        conn.commit()

        applied = {
            row[0] for row in conn.execute(
                text('SELECT version FROM schema_migrations'))
        }

        for _version_tuple, version_str, fname in files:
            if version_str in applied:
                continue

            print(f'[migrations] applying v{version_str}...')

            fpath = os.path.join(migrations_dir, fname)
            with open(fpath) as f:
                sql_content = f.read()

            statements = []
            for chunk in sql_content.split(';'):
                non_comment = [
                    line for line in chunk.splitlines()
                    if line.strip() and not line.strip().startswith('--')
                ]
                if non_comment:
                    statements.append(chunk.strip())

            try:
                for stmt in statements:
                    conn.execute(text(stmt))
                conn.execute(
                    text('INSERT INTO schema_migrations (version) '
                         'VALUES (:v)'),
                    {'v': version_str}
                )
                conn.commit()
                print(f'[migrations] v{version_str} applied.')
            except Exception:
                conn.rollback()
                raise


def cmd_create_db():
    print('Setting up the database')
    with app.app_context():
        db.create_all()


def hash_password(unhashed_password):
    return bcrypt.generate_password_hash(unhashed_password)


def reset_slug(post_id):
    post = db.session.get(Post, post_id)
    if not post:
        msg = 'No post found with id {}'.format(post_id)
        raise NotFound(msg)
    print('Resetting the slug for post {}'.format(post_id))
    print('Old slug is "{}"'.format(post.slug))
    post.slug = post.get_unique_slug(post.title)
    db.session.add(post)
    db.session.commit()
    print('New slug is "{}"'.format(post.slug))


def run():
    print('__revision__: {}'.format(__revision__))
    print('Site name: {}'.format(Config.SITENAME))
    print('Site url: {}'.format(Config.SITEURL))
    print('Host: {}'.format(Config.HOST))
    print('Port: {}'.format(Config.PORT))
    print('Debug: {}'.format(Config.DEBUG))
    if Config.CUSTOM_TEMPLATES:
        print('Custom template path: {}'.format(Config.CUSTOM_TEMPLATES))
    if Config.EXTERN_ROOT:
        print('Extern root: {}'.format(Config.EXTERN_ROOT))
    if Config.EXTRA_LINKS:
        print('Extra links: {}'.format(Config.EXTRA_LINKS))
    if Config.DEBUG:
        print('DB URI: {}'.format(Config.DB_URI))
        print('DB URI File: {}'.format(Config.DB_URI_FILE))
        print(f"Effective DB URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
        print('Secret Key: {}'.format(Config.SECRET_KEY))
    print('Local Resources: {}'.format(Config.LOCAL_RESOURCES))

    if args.create_db:
        cmd_create_db()
    elif args.hash_password is not None:
        print(hash_password(args.hash_password))
    elif args.count_posts:
        c = db.session.execute(
            db.select(db.func.count()).select_from(Post)).scalar()
        print(f'Found {c} posts.')
    elif args.reset_slug is not None:
        try:
            reset_slug(args.reset_slug)
        except NotFound as e:
            print(e.description)
    elif args.set_date is not None:
        post_id, new_date = args.set_date
        post = db.session.get(Post, post_id)
        if not post:
            print('No post found with id {}'.format(post_id))
            exit(1)
        print('Setting the date for post {}'.format(post_id))
        print('Old date is "{}"'.format(post.date))
        post.date = dateutil.parser.parse(new_date)
        db.session.add(post)
        db.session.commit()
        print('New date is "{}"'.format(post.date))
    elif args.set_last_updated_date is not None:
        post_id, new_date = args.set_last_updated_date
        post = db.session.get(Post, post_id)
        if not post:
            print('No post found with id {}'.format(post_id))
            exit(1)
        print('Setting the last updated date for post {}'.format(post_id))
        print('Old date is "{}"'.format(post.last_updated_date))
        post.last_updated_date = dateutil.parser.parse(new_date)
        db.session.add(post)
        db.session.commit()
        print('New last updated date is "{}"'.format(post.last_updated_date))
    elif args.reset_summary is not None:
        post_id = args.reset_summary
        post = db.session.get(Post, post_id)
        if not post:
            print('No post found with id {}'.format(post_id))
            exit(1)
        print('Resetting the summary for post {}'.format(post_id))
        print('Old summary is "{}"'.format(post.summary))
        post.content = post.content
        db.session.add(post)
        db.session.commit()
        print('New summary is "{}"'.format(post.summary))
    elif args.set_option is not None:
        name, value = args.set_option
        option = db.session.get(Option, name)
        if option:
            print('Setting the value for option {}'.format(name))
            print('Old value is "{}"'.format(option.value))
            option.value = value
        else:
            print('Creating option {}'.format(name))
            option = Option(name, value)
        db.session.add(option)
        db.session.commit()
        print('New value is "{}"'.format(option.value))
    elif args.clear_option is not None:
        name = args.clear_option
        option = db.session.get(Option, name)
        if not option:
            print('No option found with name {}'.format(name))
            exit(1)
        print('Clearing option {}'.format(name))
        print('Old value is "{}"'.format(option.value))
        db.session.delete(option)
        db.session.commit()
    else:
        app.run(debug=Config.DEBUG, host=Config.HOST, port=Config.PORT,
                use_reloader=Config.DEBUG)


def create_app(config=None):
    app = Flask(__name__)

    extra_loaders = []
    if Config.CUSTOM_TEMPLATES:
        extra_loaders.append(jinja2.FileSystemLoader(Config.CUSTOM_TEMPLATES))
    if Config.EXTERN_ROOT:
        extra_loaders.append(jinja2.FileSystemLoader(Config.EXTERN_ROOT))
    if extra_loaders:
        extra_loaders.append(app.jinja_loader)
        app.jinja_loader = jinja2.ChoiceLoader(extra_loaders)

    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config['SECRET_KEY'] = Config.SECRET_KEY  # for WTF-forms and login

    db_uri = 'sqlite://'
    if Config.DB_URI:
        db_uri = Config.DB_URI
    elif Config.DB_URI_FILE:
        try:
            with open(Config.DB_URI_FILE) as f:
                db_uri = f.read().strip()
        except FileNotFoundError:
            raise ConfigError(
                f'Could not find uri file "{Config.DB_URI_FILE}".')
        except PermissionError:
            raise ConfigError(
                f'Permission error when opening uri file '
                f'"{Config.DB_URI_FILE}".')
        except Exception as e:
            raise ConfigError(
                f'Error opening uri file "{Config.DB_URI_FILE}": {e}')
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri

    if config:
        app.config.update(config)

    login_manager.init_app(app)
    db.init_app(app)
    app.db = db
    bcrypt.init_app(app)

    app.context_processor(setup_options)
    app.add_template_filter(render_gfm, name='gfm')

    app.add_url_rule('/', 'index', index)
    app.add_url_rule('/login', 'login', login, methods=['GET', 'POST'])
    app.add_url_rule('/post/<slug>', 'get_post', get_post)
    app.add_url_rule('/edit/<slug>', 'edit_post', edit_post,
                     methods=['GET', 'POST'])
    app.add_url_rule('/new', 'create_new', create_new, methods=['GET', 'POST'])
    app.add_url_rule('/tags', 'list_tags', list_tags)
    app.add_url_rule('/tags/<tag_id>', 'get_tag', get_tag)
    app.add_url_rule('/page', 'list_pages', list_pages)
    app.add_url_rule('/page/<slug>', 'view_page', view_page)
    app.add_url_rule('/page/<slug>/edit', 'edit_page', edit_page,
                     methods=['GET', 'POST'])
    app.add_url_rule('/new-page', 'create_new_page', create_new_page,
                     methods=['GET', 'POST'])
    app.add_url_rule('/logout', 'logout', logout)
    app.add_url_rule('/admin', 'admin', admin, methods=['GET', 'POST'])
    app.add_url_rule('/pages/<path:filename>', 'get_page', get_page)

    return app


app = create_app()

with app.app_context():
    run_migrations(db.engine)


if __name__ == "__main__":
    run()
