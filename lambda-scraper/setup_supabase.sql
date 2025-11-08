-- ============================================================================
-- POLLYVIEW SUPABASE SCHEMA - Simple Version for Testing
-- ============================================================================
-- Run this in Supabase SQL Editor to set up your database
-- ============================================================================

-- Create the documents table
CREATE TABLE IF NOT EXISTS documents (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title TEXT NOT NULL,
  content TEXT,
  date DATE,
  source TEXT,
  jurisdiction TEXT,
  topics TEXT[] DEFAULT '{}',
  url TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  is_favorite BOOLEAN DEFAULT FALSE
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_documents_date ON documents(date DESC);
CREATE INDEX IF NOT EXISTS idx_documents_jurisdiction ON documents(jurisdiction);
CREATE INDEX IF NOT EXISTS idx_documents_source ON documents(source);
CREATE INDEX IF NOT EXISTS idx_documents_is_favorite ON documents(is_favorite);
CREATE INDEX IF NOT EXISTS idx_documents_topics ON documents USING GIN(topics);

-- Enable full-text search
CREATE INDEX IF NOT EXISTS idx_documents_title_search ON documents USING GIN(to_tsvector('english', title));
CREATE INDEX IF NOT EXISTS idx_documents_content_search ON documents USING GIN(to_tsvector('english', content));

-- Enable Row Level Security (RLS)
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if they exist
DROP POLICY IF EXISTS "Public read access" ON documents;
DROP POLICY IF EXISTS "Public insert access" ON documents;
DROP POLICY IF EXISTS "Public update access" ON documents;
DROP POLICY IF EXISTS "Public delete access" ON documents;

-- Create policies for public access (good for testing)
CREATE POLICY "Public read access" ON documents
  FOR SELECT
  USING (true);

CREATE POLICY "Public insert access" ON documents
  FOR INSERT
  WITH CHECK (true);

CREATE POLICY "Public update access" ON documents
  FOR UPDATE
  USING (true)
  WITH CHECK (true);

CREATE POLICY "Public delete access" ON documents
  FOR DELETE
  USING (true);

-- Verify setup
SELECT
  'Documents table created successfully' as status,
  COUNT(*) as current_document_count
FROM documents;
