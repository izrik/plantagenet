-- Add page table
CREATE TABLE IF NOT EXISTS page (
    id INTEGER NOT NULL PRIMARY KEY,
    title VARCHAR(100),
    slug VARCHAR(100),
    content TEXT,
    notes TEXT,
    date TIMESTAMP,
    last_updated_date TIMESTAMP NOT NULL,
    published_date TIMESTAMP,
    is_draft BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_page_slug ON page (slug)
