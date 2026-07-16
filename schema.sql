-- PositionPilot Database Schema
-- Run this to create all required tables

-- Core GTM Strategy table
CREATE TABLE IF NOT EXISTS strategy_runs (
    id SERIAL PRIMARY KEY,
    generation_run_id TEXT NOT NULL,
    agent TEXT NOT NULL,
    output JSONB,
    model_used TEXT,
    status TEXT DEFAULT 'pending_review',
    reviewed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    marketing_stage TEXT DEFAULT 'Brand Awareness (Top of Funnel)'
);

CREATE INDEX IF NOT EXISTS idx_strategy_runs_generation_run_id ON strategy_runs(generation_run_id);
CREATE INDEX IF NOT EXISTS idx_strategy_runs_status ON strategy_runs(status);
CREATE INDEX IF NOT EXISTS idx_strategy_runs_agent ON strategy_runs(agent);

-- Customer Research table
CREATE TABLE IF NOT EXISTS research_runs (
    id SERIAL PRIMARY KEY,
    generation_run_id TEXT NOT NULL,
    agent TEXT NOT NULL,
    output JSONB,
    model_used TEXT,
    status TEXT DEFAULT 'pending_review',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_research_runs_generation_run_id ON research_runs(generation_run_id);
CREATE INDEX IF NOT EXISTS idx_research_runs_status ON research_runs(status);

-- Competitive Narrative table
CREATE TABLE IF NOT EXISTS competitor_runs (
    id SERIAL PRIMARY KEY,
    generation_run_id TEXT NOT NULL,
    competitor_name TEXT,
    agent TEXT NOT NULL,
    output JSONB,
    model_used TEXT,
    run_type TEXT DEFAULT 'deep_dive',
    status TEXT DEFAULT 'pending_review',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_competitor_runs_generation_run_id ON competitor_runs(generation_run_id);
CREATE INDEX IF NOT EXISTS idx_competitor_runs_status ON competitor_runs(status);

-- Brand Voice Guardian table
CREATE TABLE IF NOT EXISTS brand_voice_runs (
    id SERIAL PRIMARY KEY,
    generation_run_id TEXT NOT NULL,
    agent TEXT NOT NULL,
    output JSONB,
    model_used TEXT,
    content_type TEXT DEFAULT 'general',
    status TEXT DEFAULT 'completed',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_brand_voice_runs_generation_run_id ON brand_voice_runs(generation_run_id);
CREATE INDEX IF NOT EXISTS idx_brand_voice_runs_status ON brand_voice_runs(status);
