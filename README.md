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

## Setting the Admin Password

```sh
python plantagenet.py --hash-password YOUR_PASSWORD
# Copy the hash string (without the b'' wrapper)
python plantagenet.py --set-option hashed_password HASH
```

After that, the password can be changed from the `/admin` page.

## Configuration

See [docs/configuration.md](docs/configuration.md) for all environment
variables and settings.

## Development

```sh
pip install -r dev_requirements.txt
./run_tests_with_coverage.sh
```

See [CLAUDE.md](CLAUDE.md) for development workflow and code conventions.

## Docker

```sh
docker build -t plantagenet .
docker run -p 8080:8080 plantagenet
```

## License

GNU Affero General Public License v3.0 — see [LICENSE](LICENSE).
