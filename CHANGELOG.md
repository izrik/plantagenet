# Changelog

All notable changes to Plantagenet are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added

- **Posts show the date that matters to a reader** (#94, closes #54). A
  post now records a published date, set the first time it is saved as
  non-draft and never overwritten afterwards, so unpublishing and
  republishing keeps the original date. The index, tag and post pages
  show the created date for a draft and the published date for a
  published post; the edit page shows both. Migration `v0.4.sql` adds
  the column and backfills it from the created date for posts that are
  already published, and on a brand-new database the migrations are
  recorded rather than run, so a fresh install no longer fails on an
  `ALTER TABLE` for a column `db.create_all()` had just created.
  Ordering and the next/previous links still follow the created date.
- **This changelog** (#100), with the releases back to v0.1 condensed
  from the GitHub release notes and the git history.

### Changed

- Extra navbar links are now separated from the built-in ones by a
  divider, instead of running on from them.
- GitPython 3.1.62 and pytest 9.0.3, both patch releases closing known
  vulnerabilities (#97, closes #96).
- Werkzeug 3.1.9, closing CVE-2026-102598: `safe_join` accepted Windows
  special device names with an empty ADS marker, so a request for a file
  served by `send_from_directory` — the `--extern-root` pages and the
  static assets — could hang on NTFS (#103, closes #102). The check
  script no longer suppresses CVE-2026-4539, which a patched Pygments
  has since fixed.
- The agent documentation was split up (#95, closes #93; #99, closes
  #98): `CLAUDE.md` is a short entry point with `AGENTS.md` as a symlink
  to it, the details live in `docs/key-files.md`,
  `docs/configuration.md` and `docs/testing.md`, and `README.md` gained
  a quick start and a pointer to the configuration reference.

## [v1.1.1] - 2026-04-08

A startup fix release: a fresh install against PostgreSQL could not get
through its migrations.

### Fixed

- A fresh install on PostgreSQL starts up (#86). The `schema_migrations`
  bookkeeping table was created with SQLite's `datetime('now')` default
  and the `v0.3` migration declared a `DATETIME` column; both are now
  standard SQL (`CURRENT_TIMESTAMP`, `TIMESTAMP`), which PostgreSQL and
  MySQL accept.
- Pages created on PostgreSQL get a primary key (#86). `db.create_all()`
  now runs before the migrations, so SQLAlchemy builds the tables with
  the backend's own types (`SERIAL` rather than a plain integer) before
  any migration touches them.
- Migration logging names the file being applied and prints each
  statement before it runs, so a failure says which statement failed
  (#86).

## [v1.1] - 2026-04-07

The site becomes configurable from the browser: an admin page for the
site name, the password and the navbar links, plus error pages and flash
messages that look like the rest of the site.

### Added

- An admin page at `/admin` for the site name, the admin password and
  extra navbar links (#82, #84, closes #8). Changing the password no
  longer means running `--hash-password` and `--set-option` on the
  server.
- Styled error pages for 400, 401, 403, 404, 500 and 503 responses
  (#85).
- Markdown tables are styled to match GitHub's rendering (#83).

### Changed

- Flash messages appear on every page rather than only the admin page,
  and an `error` message renders as a Bootstrap danger alert (#85).
- The footer stays at the bottom of the viewport on short pages (#85).
- Markdown is rendered by `pycmarkgfm`, a binding for GitHub's own
  cmark-gfm, in place of the unmaintained `py-gfm`; this also silences a
  `DeprecationWarning` on every render (#83).
- The post, page, admin and login forms use a proper Bootstrap 3
  vertical form layout (#82).

### Fixed

- The version and revision in the page footer are no longer hard-coded
  (#76). The version comes from `__version__` and falls back to
  `unknown`; the revision comes from the git checkout — with a `-dirty`
  suffix when the working tree has uncommitted changes — or from
  `PLANTAGENET_REVISION` in a built image, which the Dockerfile sets.

## [v1.0] - 2026-04-03

First stable release. Pages move into the database, and schema changes
apply themselves at startup.

### Added

- Pages are stored in the database and edited in the browser, like posts
  (#75). `/page` lists them, `/page/<slug>` views one, and `/new-page`
  and `/page/<slug>/edit` create and edit them in Markdown. Until now a
  page had to be a file in an `--extern-root` directory.
- Schema changes apply themselves (#75). The SQL files in `migrations/`
  are sorted by version and the pending ones run at startup, each in its
  own transaction, with what has been applied recorded in a
  `schema_migrations` table. The file format and workflow are documented
  in `migrations/README.md`.

### Fixed

- `/tags` no longer returns a 500 error (#74). Post counts are computed
  in the view and passed to the template, instead of being queried from
  the template in a way SQLAlchemy 2.0 no longer supports.

## [v0.4] - 2026-03-30

Content and navigation can come from outside the repository, and the
project moves to Python 3.12.

### Added

- `--extern-root` / `PLANTAGENET_EXTERN_ROOT` serves pages and assets
  from a directory outside the checkout (#72). A `.html` file under
  `<root>/pages` is rendered as a template at `/pages/<name>`, anything
  else there is served as a file, and templates in the root override the
  built-in ones — so a site can be customised without forking.
- `--extra-links` / `PLANTAGENET_EXTRA_LINKS` adds links to the navbar,
  as a comma-separated list of `Label:URL` pairs (#72). The
  `extra_links` option in the database takes precedence over both, so
  the links can be changed with `--set-option` without a restart.

### Changed

- Runs on Python 3.12 (#73). The image is based on `python:3.12-alpine`,
  and Flask 3.1, SQLAlchemy 2.0 with Flask-SQLAlchemy 3.1, bcrypt 4.3
  with Flask-Bcrypt 1.0.1, gunicorn 23.0, psycopg2 2.9.10 and
  python-dateutil 2.9 come with it; unused dependencies were dropped.
- GitPython 3.1.46 closes several CVEs reported against the pinned
  version (#73).
- Checks run on GitHub Actions for every pull request and every push to
  `master`, with coverage reported to Coveralls (#73). The local check
  script gained `bandit` and `pip-audit` and dropped `safety`,
  `markdownlint`, `csslint` and `dockerfile_lint`, replacing the
  Markdown linter with `pymarkdownlnt`.

## [v0.3] - 2021-09-06

Repairs what the Python 3 upgrade in v0.2 left broken.

### Fixed

- The index, tag list and tag pages render again (#71). They called the
  Python 2 iterator method `.next`, which does not exist in Python 3, so
  every one of them raised.
- Markdown is rendered again (#71). `py-gfm` 1.0.2 no longer registers
  itself under the extension name `gfm`, so post and page content came
  back empty or raised; the extension is now passed as an object.
- `python plantagenet.py` serves the site again instead of printing the
  post count and exiting (#71). `--count-posts` is a flag, so it is
  `False` rather than `None` when absent, and the check for it matched
  on every run.

## [v0.2] - 2021-08-25

Python 3, PostgreSQL, and a much smaller image.

### Added

- `--db-uri-file` / `PLANTAGENET_DB_URI_FILE` reads the database URI
  from a file, so a connection string containing a password need not be
  passed as an argument or an environment variable (#70). A missing or
  unreadable file is reported as a configuration error naming the file.
- `--count-posts` prints the number of posts, a quick check that the
  configured database is reachable (#70). In this release the check for
  the flag matches on every run, so it is only usable as intended from
  v0.3 onwards.

### Changed

- Runs on Python 3.8 on Alpine Linux (`python:3.8.11-alpine3.14`),
  drastically reducing the size of the image (#70).
- PostgreSQL is the expected backend: the image installs `libpq` and
  `psycopg2` (#70).
- `PLANTAGENET_DB_URI` no longer defaults to `sqlite:////tmp/blog.db`.
  With no URI and no URI file configured the app now runs against an
  in-memory SQLite database, so an upgraded deployment that relied on
  the old default must set the URI explicitly to keep its posts (#70).
- Dependencies upgraded to clear known vulnerabilities, among them Flask
  2.0.1, SQLAlchemy 1.4, Jinja2 3.0, GitPython 3.0 and py-gfm 1.0.2
  (#70).

## [v0.1] - 2018-06-18

The first versioned release of Plantagenet, a Python blogging system
built on Flask.

### Added

- Blog posts written in GitHub-flavored Markdown, with a title, a slug,
  a summary, private notes, tags and a draft flag. The index pages
  through them newest first, `/post/<slug>` shows one, `/tags` lists the
  tags and `/tags/<tag>` the posts under one.
- A single admin user, who logs in at `/login` and writes and edits
  posts in the browser at `/new` and `/edit/<slug>`. Drafts are visible
  only once logged in.
- Configuration from `PLANTAGENET_*` environment variables or the
  matching command-line arguments: host, port, debug, database URI, site
  name, site URL, author, secret key, a directory of custom templates
  overriding the built-in ones, and a local-resources mode that serves
  Bootstrap and jQuery from the app itself rather than from a CDN.
- Maintenance commands: `--create-db`, `--create-secret-key`,
  `--hash-password`, `--set-option` and `--clear-option`,
  `--reset-slug`, `--reset-summary`, `--set-date` and
  `--set-last-updated-date`.
- A Docker image that creates the database if needed and serves the app
  with gunicorn.

[Unreleased]: https://github.com/izrik/plantagenet/compare/v1.1.1...HEAD
[v1.1.1]: https://github.com/izrik/plantagenet/compare/v1.1...v1.1.1
[v1.1]: https://github.com/izrik/plantagenet/compare/v1.0...v1.1
[v1.0]: https://github.com/izrik/plantagenet/compare/v0.4...v1.0
[v0.4]: https://github.com/izrik/plantagenet/compare/v0.3...v0.4
[v0.3]: https://github.com/izrik/plantagenet/compare/v0.2...v0.3
[v0.2]: https://github.com/izrik/plantagenet/compare/v0.1...v0.2
[v0.1]: https://github.com/izrik/plantagenet/releases/tag/v0.1
