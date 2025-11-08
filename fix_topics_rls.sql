-- Fix Row Level Security for document_topics table
-- This allows the scraper to insert topic relationships

-- Allow public insert to document_topics
CREATE POLICY "Public insert document topics" ON document_topics
  FOR INSERT
  WITH CHECK (true);
