-- GALPATH · Supabase Schema
-- Run this in Supabase SQL Editor → New Query

-- Sessions table
CREATE TABLE IF NOT EXISTS galpath_sessions (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  session_id TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  entry_type TEXT,
  motive TEXT,
  skill TEXT,
  situation TEXT,
  stage_reached INTEGER DEFAULT 0,
  completed BOOLEAN DEFAULT FALSE
);

-- Outcomes table
CREATE TABLE IF NOT EXISTS galpath_outcomes (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  session_id TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  path_chosen TEXT,
  satisfaction_rating INTEGER CHECK (satisfaction_rating BETWEEN 1 AND 5),
  feedback_text TEXT
);

-- Follow-up table (7-day outcome tracking)
CREATE TABLE IF NOT EXISTS galpath_followup (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  session_id TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  followup_sent_at TIMESTAMPTZ,
  took_first_step BOOLEAN,
  followup_notes TEXT
);

-- Enable Row Level Security (anonymous access for MVP)
ALTER TABLE galpath_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE galpath_outcomes ENABLE ROW LEVEL SECURITY;
ALTER TABLE galpath_followup ENABLE ROW LEVEL SECURITY;

-- Allow anonymous inserts (MVP mode)
CREATE POLICY "anon insert sessions" ON galpath_sessions FOR INSERT TO anon WITH CHECK (true);
CREATE POLICY "anon insert outcomes" ON galpath_outcomes FOR INSERT TO anon WITH CHECK (true);

-- Useful views for the metrics dashboard
CREATE OR REPLACE VIEW galpath_metrics AS
SELECT
  COUNT(*) AS total_sessions,
  COUNT(*) FILTER (WHERE completed = TRUE) AS completed_sessions,
  ROUND(COUNT(*) FILTER (WHERE completed = TRUE)::NUMERIC / NULLIF(COUNT(*), 0) * 100, 1) AS completion_rate,
  COUNT(DISTINCT motive) AS unique_motives
FROM galpath_sessions;
