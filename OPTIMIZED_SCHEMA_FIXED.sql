-- ============================================================================
-- OPTIMIZED SCHEMA FOR LARGE-SCALE MULTI-STATE/INTERNATIONAL WEB SCRAPING
-- ============================================================================
-- This schema is designed for:
-- - Millions to billions of documents
-- - 50+ US states + international jurisdictions
-- - Multiple scraper sources per jurisdiction
-- - Efficient querying and deduplication
-- - Partitioning for performance
-- - Analytics and engagement tracking
-- ============================================================================

-- ============================================================================
-- 1. GEOGRAPHY HIERARCHY (normalized jurisdictions)
-- ============================================================================

-- Countries table
CREATE TABLE countries (
  id SERIAL PRIMARY KEY,
  code VARCHAR(2) NOT NULL UNIQUE, -- ISO 3166-1 alpha-2 (US, CA, GB)
  name TEXT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- States/Provinces table
CREATE TABLE states (
  id SERIAL PRIMARY KEY,
  country_id INTEGER NOT NULL REFERENCES countries(id),
  code VARCHAR(10) NOT NULL, -- State abbreviation (MD, CA, NY)
  name TEXT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(country_id, code)
);

-- Cities/Counties table (optional, for granular filtering)
CREATE TABLE localities (
  id SERIAL PRIMARY KEY,
  state_id INTEGER NOT NULL REFERENCES states(id),
  name TEXT NOT NULL,
  locality_type VARCHAR(20) NOT NULL, -- 'city', 'county', 'municipality'
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for geography
CREATE INDEX idx_states_country_id ON states(country_id);
CREATE INDEX idx_localities_state_id ON localities(state_id);

-- ============================================================================
-- 2. SOURCES (normalized government bodies)
-- ============================================================================

CREATE TABLE sources (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  source_type VARCHAR(50) NOT NULL, -- 'legislature', 'council', 'commission', 'board', etc.
  state_id INTEGER REFERENCES states(id),
  locality_id INTEGER REFERENCES localities(id),
  website_url TEXT,
  scraper_config JSONB, -- Scraper-specific settings
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for sources
CREATE INDEX idx_sources_state_id ON sources(state_id);
CREATE INDEX idx_sources_locality_id ON sources(locality_id);
CREATE INDEX idx_sources_type ON sources(source_type);
CREATE INDEX idx_sources_active ON sources(is_active) WHERE is_active = TRUE;

-- ============================================================================
-- 3. TOPICS (normalized taxonomy)
-- ============================================================================

CREATE TABLE topics (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL UNIQUE,
  slug VARCHAR(100) NOT NULL UNIQUE, -- URL-friendly: 'public-safety', 'housing'
  description TEXT,
  parent_id INTEGER REFERENCES topics(id), -- For hierarchical topics
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for topics
CREATE INDEX idx_topics_parent_id ON topics(parent_id);

-- ============================================================================
-- 4. DOCUMENTS (main table - PARTITIONED by date)
-- ============================================================================
-- FIXED: Primary key now includes document_date for partitioning compatibility

CREATE TABLE documents (
  id UUID DEFAULT gen_random_uuid(),
  document_date DATE NOT NULL, -- Moved up for partition key

  -- Core content
  title TEXT NOT NULL,
  content TEXT, -- Consider moving to separate table for large content
  content_hash VARCHAR(64), -- SHA-256 for deduplication
  summary TEXT, -- AI-generated summary for quick preview

  -- Dates
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

  -- Relationships
  source_id INTEGER NOT NULL REFERENCES sources(id),
  state_id INTEGER NOT NULL REFERENCES states(id), -- Denormalized for faster queries
  country_id INTEGER NOT NULL REFERENCES countries(id), -- Denormalized

  -- Metadata
  url TEXT,
  original_url TEXT, -- Original source URL before any redirects
  document_type VARCHAR(50), -- 'agenda', 'minutes', 'resolution', 'ordinance'
  status VARCHAR(20) DEFAULT 'published', -- 'draft', 'published', 'archived'

  -- User engagement
  is_favorite BOOLEAN DEFAULT FALSE,
  view_count INTEGER DEFAULT 0,
  importance_score FLOAT DEFAULT 0.0, -- AI-calculated relevance score

  -- Scraping metadata
  scraper_version VARCHAR(20),
  scraped_at TIMESTAMP WITH TIME ZONE,
  last_verified_at TIMESTAMP WITH TIME ZONE,

  -- FIXED: Composite primary key includes partition key
  PRIMARY KEY (id, document_date)

) PARTITION BY RANGE (document_date);

-- Create partitions for each year (example for 2024-2030)
-- This DRAMATICALLY improves query performance for date-filtered queries
CREATE TABLE documents_2024 PARTITION OF documents
  FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');

CREATE TABLE documents_2025 PARTITION OF documents
  FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');

CREATE TABLE documents_2026 PARTITION OF documents
  FOR VALUES FROM ('2026-01-01') TO ('2027-01-01');

CREATE TABLE documents_2027 PARTITION OF documents
  FOR VALUES FROM ('2027-01-01') TO ('2028-01-01');

CREATE TABLE documents_2028 PARTITION OF documents
  FOR VALUES FROM ('2028-01-01') TO ('2029-01-01');

CREATE TABLE documents_2029 PARTITION OF documents
  FOR VALUES FROM ('2029-01-01') TO ('2030-01-01');

CREATE TABLE documents_2030 PARTITION OF documents
  FOR VALUES FROM ('2030-01-01') TO ('2031-01-01');

-- Create default partition for future dates
CREATE TABLE documents_default PARTITION OF documents DEFAULT;

-- ============================================================================
-- 5. DOCUMENT-TOPIC RELATIONSHIP (many-to-many)
-- ============================================================================

CREATE TABLE document_topics (
  document_id UUID NOT NULL,
  document_date DATE NOT NULL, -- ADDED: Required for foreign key to partitioned table
  topic_id INTEGER NOT NULL REFERENCES topics(id),
  confidence FLOAT DEFAULT 1.0, -- AI confidence score (0.0-1.0)
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  PRIMARY KEY (document_id, document_date, topic_id),
  FOREIGN KEY (document_id, document_date) REFERENCES documents(id, document_date) ON DELETE CASCADE
);

-- Indexes for document_topics
CREATE INDEX idx_document_topics_topic_id ON document_topics(topic_id);
CREATE INDEX idx_document_topics_confidence ON document_topics(confidence DESC);

-- ============================================================================
-- 6. SCRAPER RUNS (track scraping jobs)
-- ============================================================================

CREATE TABLE scraper_runs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  source_id INTEGER NOT NULL REFERENCES sources(id),
  status VARCHAR(20) NOT NULL, -- 'running', 'success', 'failed', 'partial'
  started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  completed_at TIMESTAMP WITH TIME ZONE,
  documents_found INTEGER DEFAULT 0,
  documents_added INTEGER DEFAULT 0,
  documents_updated INTEGER DEFAULT 0,
  error_message TEXT,
  scraper_version VARCHAR(20)
);

-- Indexes for scraper_runs
CREATE INDEX idx_scraper_runs_source_id ON scraper_runs(source_id);
CREATE INDEX idx_scraper_runs_started_at ON scraper_runs(started_at DESC);
CREATE INDEX idx_scraper_runs_status ON scraper_runs(status);

-- ============================================================================
-- 7. USER FAVORITES (if you add authentication later)
-- ============================================================================

-- Note: For now, is_favorite in documents table is global
-- When you add auth, replace with this user-specific table:

-- CREATE TABLE user_favorites (
--   user_id UUID NOT NULL REFERENCES auth.users(id),
--   document_id UUID NOT NULL,
--   document_date DATE NOT NULL,
--   created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
--   PRIMARY KEY (user_id, document_id, document_date),
--   FOREIGN KEY (document_id, document_date) REFERENCES documents(id, document_date) ON DELETE CASCADE
-- );

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- Documents table indexes
CREATE INDEX idx_documents_source_id ON documents(source_id);
CREATE INDEX idx_documents_state_id ON documents(state_id);
CREATE INDEX idx_documents_country_id ON documents(country_id);
CREATE INDEX idx_documents_date ON documents(document_date DESC);
CREATE INDEX idx_documents_created_at ON documents(created_at DESC);
CREATE INDEX idx_documents_content_hash ON documents(content_hash) WHERE content_hash IS NOT NULL;
CREATE INDEX idx_documents_status ON documents(status);
CREATE INDEX idx_documents_type ON documents(document_type);
CREATE INDEX idx_documents_importance ON documents(importance_score DESC);

-- Full-text search indexes (GIN)
CREATE INDEX idx_documents_title_search ON documents USING GIN(to_tsvector('english', title));
CREATE INDEX idx_documents_content_search ON documents USING GIN(to_tsvector('english', COALESCE(content, '')));

-- Composite indexes for common queries
CREATE INDEX idx_documents_state_date ON documents(state_id, document_date DESC);
CREATE INDEX idx_documents_country_date ON documents(country_id, document_date DESC);
CREATE INDEX idx_documents_source_date ON documents(source_id, document_date DESC);

-- ============================================================================
-- FUNCTIONS FOR COMMON QUERIES
-- ============================================================================

-- Full-text search with ranking (improved version)
CREATE OR REPLACE FUNCTION search_documents(
  search_query TEXT,
  country_filter INTEGER DEFAULT NULL,
  state_filter INTEGER DEFAULT NULL,
  limit_results INTEGER DEFAULT 50
)
RETURNS TABLE (
  id UUID,
  title TEXT,
  summary TEXT,
  document_date DATE,
  source_name TEXT,
  state_name TEXT,
  country_name TEXT,
  rank REAL
) AS $$
BEGIN
  RETURN QUERY
  SELECT
    d.id,
    d.title,
    d.summary,
    d.document_date,
    s.name AS source_name,
    st.name AS state_name,
    c.name AS country_name,
    ts_rank(
      to_tsvector('english', d.title || ' ' || COALESCE(d.content, '') || ' ' || COALESCE(d.summary, '')),
      plainto_tsquery('english', search_query)
    ) AS rank
  FROM documents d
  JOIN sources s ON d.source_id = s.id
  JOIN states st ON d.state_id = st.id
  JOIN countries c ON d.country_id = c.id
  WHERE
    to_tsvector('english', d.title || ' ' || COALESCE(d.content, '') || ' ' || COALESCE(d.summary, ''))
    @@ plainto_tsquery('english', search_query)
    AND (country_filter IS NULL OR d.country_id = country_filter)
    AND (state_filter IS NULL OR d.state_id = state_filter)
    AND d.status = 'published'
  ORDER BY rank DESC, d.document_date DESC
  LIMIT limit_results;
END;
$$ LANGUAGE plpgsql;

-- Get documents by topic
CREATE OR REPLACE FUNCTION get_documents_by_topic(
  topic_slug_param VARCHAR(100),
  limit_results INTEGER DEFAULT 50
)
RETURNS TABLE (
  id UUID,
  title TEXT,
  document_date DATE,
  source_name TEXT,
  state_name TEXT
) AS $$
BEGIN
  RETURN QUERY
  SELECT
    d.id,
    d.title,
    d.document_date,
    s.name AS source_name,
    st.name AS state_name
  FROM documents d
  JOIN document_topics dt ON d.id = dt.document_id AND d.document_date = dt.document_date
  JOIN topics t ON dt.topic_id = t.id
  JOIN sources s ON d.source_id = s.id
  JOIN states st ON d.state_id = st.id
  WHERE t.slug = topic_slug_param
    AND d.status = 'published'
  ORDER BY dt.confidence DESC, d.document_date DESC
  LIMIT limit_results;
END;
$$ LANGUAGE plpgsql;

-- Check for duplicate documents by hash
CREATE OR REPLACE FUNCTION find_duplicate_document(
  content_hash_param VARCHAR(64)
)
RETURNS TABLE (
  id UUID,
  document_date DATE
) AS $$
BEGIN
  RETURN QUERY
  SELECT d.id, d.document_date
  FROM documents d
  WHERE d.content_hash = content_hash_param
  LIMIT 1;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- ROW LEVEL SECURITY (RLS)
-- ============================================================================

-- Enable RLS on tables
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE document_topics ENABLE ROW LEVEL SECURITY;
ALTER TABLE scraper_runs ENABLE ROW LEVEL SECURITY;

-- Public read access (anyone can view published documents)
CREATE POLICY "Public read published documents" ON documents
  FOR SELECT
  USING (status = 'published');

-- Public read access to topics relationship
CREATE POLICY "Public read document topics" ON document_topics
  FOR SELECT
  USING (true);

-- Scraper write access (will need to update when you add auth)
CREATE POLICY "Public insert documents" ON documents
  FOR INSERT
  WITH CHECK (true);

CREATE POLICY "Public update documents" ON documents
  FOR UPDATE
  USING (true)
  WITH CHECK (true);

-- Public read access to scraper runs
CREATE POLICY "Public read scraper runs" ON scraper_runs
  FOR SELECT
  USING (true);

CREATE POLICY "Public insert scraper runs" ON scraper_runs
  FOR INSERT
  WITH CHECK (true);

CREATE POLICY "Public update scraper runs" ON scraper_runs
  FOR UPDATE
  USING (true)
  WITH CHECK (true);

-- ============================================================================
-- SEED DATA (sample geography and topics)
-- ============================================================================

-- Insert United States
INSERT INTO countries (code, name) VALUES ('US', 'United States');

-- Insert sample US states (all 50)
INSERT INTO states (country_id, code, name)
SELECT
  (SELECT id FROM countries WHERE code = 'US'),
  state_code,
  state_name
FROM (VALUES
  ('AL', 'Alabama'),
  ('AK', 'Alaska'),
  ('AZ', 'Arizona'),
  ('AR', 'Arkansas'),
  ('CA', 'California'),
  ('CO', 'Colorado'),
  ('CT', 'Connecticut'),
  ('DE', 'Delaware'),
  ('FL', 'Florida'),
  ('GA', 'Georgia'),
  ('HI', 'Hawaii'),
  ('ID', 'Idaho'),
  ('IL', 'Illinois'),
  ('IN', 'Indiana'),
  ('IA', 'Iowa'),
  ('KS', 'Kansas'),
  ('KY', 'Kentucky'),
  ('LA', 'Louisiana'),
  ('ME', 'Maine'),
  ('MD', 'Maryland'),
  ('MA', 'Massachusetts'),
  ('MI', 'Michigan'),
  ('MN', 'Minnesota'),
  ('MS', 'Mississippi'),
  ('MO', 'Missouri'),
  ('MT', 'Montana'),
  ('NE', 'Nebraska'),
  ('NV', 'Nevada'),
  ('NH', 'New Hampshire'),
  ('NJ', 'New Jersey'),
  ('NM', 'New Mexico'),
  ('NY', 'New York'),
  ('NC', 'North Carolina'),
  ('ND', 'North Dakota'),
  ('OH', 'Ohio'),
  ('OK', 'Oklahoma'),
  ('OR', 'Oregon'),
  ('PA', 'Pennsylvania'),
  ('RI', 'Rhode Island'),
  ('SC', 'South Carolina'),
  ('SD', 'South Dakota'),
  ('TN', 'Tennessee'),
  ('TX', 'Texas'),
  ('UT', 'Utah'),
  ('VT', 'Vermont'),
  ('VA', 'Virginia'),
  ('WA', 'Washington'),
  ('WV', 'West Virginia'),
  ('WI', 'Wisconsin'),
  ('WY', 'Wyoming')
) AS state_data(state_code, state_name);

-- Insert sample topics
INSERT INTO topics (name, slug, description) VALUES
  ('Public Safety', 'public-safety', 'Police, fire, emergency services'),
  ('Housing', 'housing', 'Affordable housing, development, zoning'),
  ('Transportation', 'transportation', 'Roads, transit, infrastructure'),
  ('Education', 'education', 'Schools, universities, education policy'),
  ('Budget', 'budget', 'Fiscal matters, appropriations, taxation'),
  ('Health', 'health', 'Public health, healthcare services'),
  ('Environment', 'environment', 'Environmental policy, sustainability'),
  ('Economic Development', 'economic-development', 'Business, jobs, economic growth'),
  ('Zoning', 'zoning', 'Land use, development, planning'),
  ('Infrastructure', 'infrastructure', 'Public works, utilities, facilities'),
  ('Social Services', 'social-services', 'Welfare, assistance programs'),
  ('Recreation', 'recreation', 'Parks, recreation, cultural programs');

-- ============================================================================
-- NOTES ON PARTITIONING FIX
-- ============================================================================

-- CHANGES FROM ORIGINAL:
-- 1. PRIMARY KEY changed from (id) to (id, document_date)
--    - Required by PostgreSQL for partitioned tables
--    - Ensures partition key is part of primary key
--
-- 2. document_topics table updated:
--    - Added document_date column
--    - Foreign key now references (document_id, document_date)
--    - Primary key includes document_date
--
-- 3. find_duplicate_document function updated:
--    - Returns both id and document_date (needed for foreign keys)
--
-- PERFORMANCE IMPACT:
-- - Minimal - composite primary key is still indexed
-- - Queries by id alone still fast (covered by index)
-- - Joins require both id and document_date (slightly more verbose)
--
-- MIGRATION NOTE:
-- - Scrapers need minor update to pass document_date when creating document_topics
-- - No other changes required

-- ============================================================================
-- BACKUP & MAINTENANCE
-- ============================================================================

-- Auto-vacuum settings (add to Supabase dashboard or postgresql.conf)
-- ALTER TABLE documents SET (autovacuum_vacuum_scale_factor = 0.05);
-- ALTER TABLE document_topics SET (autovacuum_vacuum_scale_factor = 0.1);

-- Create new partitions annually (automate with cron or Lambda)
-- CREATE TABLE documents_2031 PARTITION OF documents
--   FOR VALUES FROM ('2031-01-01') TO ('2032-01-01');
