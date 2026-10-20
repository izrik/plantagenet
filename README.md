# Plantagenet

A Python blogging system built on Flask.

<https://github.com/izrik/plantagenet>

## Quick Start

```sh
# Setup
python3 -m venv venv && . venv/bin/activate
pip install -r requirements.txt

# Create database and run
python plantagenet.py --db-uri sqlite:///plantagenet.db --create-db
python plantagenet.py --db-uri sqlite:///plantagenet.db --debug
```

The server runs at `http://127.0.0.1:1177` by default.

## Creating the First Administrator

Users log in with an email address and their own password. The first
administrator has to be created on the server, from the command line:

```sh
python plantagenet.py --db-uri sqlite:///plantagenet.db \
    --create-admin you@example.com --name "Your Name"
```

The password is read from the terminal, and must be at least 8 characters
long. Other user-management commands are `--create-user EMAIL`,
`--set-user-password EMAIL` and `--list-users`.

After that, administrators manage accounts from the `/users` page, and every
user can change their own name and password on the `/account` page.
Administrators can also edit site settings on the `/admin` page; regular users
can write and edit posts and pages but cannot do either of those.

## Configuration

See [docs/configuration.md](docs/configuration.md) for all environment
variables and settings.

## Development

```sh
pip install -r dev_requirements.txt
./run_tests_with_coverage.sh
```

See [CLAUDE.md](CLAUDE.md) for development workflow and code conventions,
and [CHANGELOG.md](CHANGELOG.md) for what changed in each release.

## Reporting a Vulnerability

Please don't open a public issue — see [SECURITY.md](SECURITY.md) for how
to report a security problem privately, and what is in scope.

## Docker

```sh
docker build -t plantagenet .
docker run -p 8080:8080 plantagenet
```

## License

GNU Affero General Public License v3.0 — see [LICENSE](LICENSE).
