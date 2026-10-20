-- Add the users table and retire the site-wide password
CREATE TABLE IF NOT EXISTS users (
    id INTEGER NOT NULL PRIMARY KEY,
    email VARCHAR(100) NOT NULL,
    name VARCHAR(100) NOT NULL,
    hashed_password VARCHAR(100) NOT NULL,
    is_admin BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_users_email ON users (email);

-- The site-wide password is no longer used. Each user has their own, and the
-- first administrator is created on the server with
-- "plantagenet.py --create-admin EMAIL".
DELETE FROM option WHERE name = 'hashed_password'
