-- WARNING: These statements permanently delete data. Run only in a test database.
-- Suggested usage: paste into the Supabase SQL editor or psql when you need a clean slate.

-- ---------------------------------------------------------------------------
-- Option A: Reset only scraped content while preserving geography/source seeds
-- ---------------------------------------------------------------------------
TRUNCATE TABLE document_topics RESTART IDENTITY CASCADE;
TRUNCATE TABLE documents RESTART IDENTITY CASCADE;
TRUNCATE TABLE scraper_runs RESTART IDENTITY CASCADE;

-- ---------------------------------------------------------------------------
-- Option B: Full reset (drops all optimized-schema content and lookup records)
-- Run ONLY if you are ready to re-seed countries/states/sources/topics.
-- ---------------------------------------------------------------------------
TRUNCATE TABLE document_topics,
               documents,
               scraper_runs,
               sources,
               localities,
               states,
               countries,
               topics
RESTART IDENTITY CASCADE;

-- Notes:
-- - TRUNCATE on the partitioned "documents" table clears all yearly partitions.
-- - RESTART IDENTITY resets any SERIAL sequences tied to the truncated tables.
-- - CASCADE ensures dependent rows are removed even with foreign-key constraints.
