# Configuration

Settings live on the `Config` class in `plantagenet.py` and come from
`PLANTAGENET_*` environment variables, overridable by command-line flags (see
`--help`).

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PLANTAGENET_SECRET_KEY` | `'secret'` | Flask secret key for session signing |
| `PLANTAGENET_HOST` | `'127.0.0.1'` | Host address to bind to |
| `PLANTAGENET_PORT` | `1177` | Port to listen on |
| `PLANTAGENET_DEBUG` | `False` | Enable Flask debug mode |
| `PLANTAGENET_DB_URI` | — | SQLAlchemy database URI |
| `PLANTAGENET_DB_URI_FILE` | — | Path to file containing database URI |
| `PLANTAGENET_SITENAME` | `'Site Name'` | Site name shown in header |
| `PLANTAGENET_SITEURL` | `'http://localhost:1177'` | Canonical site URL |
| `PLANTAGENET_CUSTOM_TEMPLATES` | — | Path to custom templates directory |
| `PLANTAGENET_AUTHOR` | `'The Author'` | Default author name for posts |
| `PLANTAGENET_LOCAL_RESOURCES` | `False` | Serve Bootstrap CSS locally |
| `PLANTAGENET_EXTERN_ROOT` | — | External root path for assets |
| `PLANTAGENET_EXTRA_LINKS` | — | Additional navbar links |

## Runtime Overrides

Some settings (site name, site URL, author, extra links) can also be
overridden at runtime via the `Option` table, which takes precedence over
`Config`. Use the admin interface or the `--set-option` CLI flag to update
these values.

## Database Configuration

If neither `PLANTAGENET_DB_URI` nor `PLANTAGENET_DB_URI_FILE` is set, the
application defaults to an in-memory SQLite database (`:memory:`), which is
useful for testing but loses data on restart.

Supported databases:

- SQLite: `sqlite:///path/to/database.db`
- MySQL: `mysql://user:password@host/database`
- PostgreSQL: `postgresql://user:password@host/database`
