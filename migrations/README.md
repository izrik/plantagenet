# Migrations

This folder contains SQL migration scripts that are applied automatically at
application startup.

## Naming Convention

Migration files must be named with a semantic version prefix followed by
`.sql`, for example:

- `v0.1.sql`
- `v1.0.0.sql`
- `v1.2.3.sql`

Files not matching this pattern are ignored.

> **Warning:** The version numbers in migration filenames do **not**
> necessarily correspond to the software project's version numbers. They are
> an independent sequence used solely to order and track which migrations have
> been applied.

## How It Works

Migrations are tracked in a `schema_migrations` table in the database. Each
migration is applied once, in version order, and recorded there. To add a new
migration, create a new `.sql` file with a higher version number than any
existing file.
