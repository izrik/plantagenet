-- Add published_date to post, backfilling it for already-published posts
ALTER TABLE post ADD COLUMN published_date TIMESTAMP;

UPDATE post SET published_date = date WHERE is_draft = FALSE
