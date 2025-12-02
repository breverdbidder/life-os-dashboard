-- =====================================================
-- LIFE OS ADHD TRACKING - SCHEMA MIGRATION
-- Run in Supabase SQL Editor: 
-- https://supabase.com/dashboard/project/mocerqjnksmhcjzxrewo/sql/new
-- =====================================================
-- Created: 2025-12-02
-- Purpose: Enhance tables for XGBoost ADHD intervention model
-- =====================================================

-- =====================================================
-- 1. DAILY_METRICS ENHANCEMENTS
-- =====================================================
-- Add columns for ADHD tracking

ALTER TABLE daily_metrics 
ADD COLUMN IF NOT EXISTS context_switches INTEGER DEFAULT 0;

ALTER TABLE daily_metrics 
ADD COLUMN IF NOT EXISTS domains JSONB DEFAULT '{}';

ALTER TABLE daily_metrics 
ADD COLUMN IF NOT EXISTS peak_focus_hours TEXT[];

ALTER TABLE daily_metrics 
ADD COLUMN IF NOT EXISTS intervention_count INTEGER DEFAULT 0;

ALTER TABLE daily_metrics 
ADD COLUMN IF NOT EXISTS session_recommendation TEXT;

COMMENT ON COLUMN daily_metrics.context_switches IS 'Number of topic/task switches - ADHD risk indicator';
COMMENT ON COLUMN daily_metrics.domains IS 'Distribution of time across domains: {BUSINESS: 7, MICHAEL: 3}';
COMMENT ON COLUMN daily_metrics.peak_focus_hours IS 'Hours when focus was highest';
COMMENT ON COLUMN daily_metrics.intervention_count IS 'Number of ADHD interventions triggered';
COMMENT ON COLUMN daily_metrics.session_recommendation IS 'ML model recommendation for the day';

-- =====================================================
-- 2. INSIGHTS ENHANCEMENTS
-- =====================================================
-- Add action tracking for process improvements

ALTER TABLE insights 
ADD COLUMN IF NOT EXISTS action_taken TEXT;

ALTER TABLE insights 
ADD COLUMN IF NOT EXISTS lesson_learned TEXT;

ALTER TABLE insights 
ADD COLUMN IF NOT EXISTS recurrence_count INTEGER DEFAULT 0;

ALTER TABLE insights 
ADD COLUMN IF NOT EXISTS last_occurred_at TIMESTAMPTZ;

COMMENT ON COLUMN insights.action_taken IS 'What was done to address this insight';
COMMENT ON COLUMN insights.lesson_learned IS 'Key takeaway from this insight';
COMMENT ON COLUMN insights.recurrence_count IS 'How many times this pattern has occurred';
COMMENT ON COLUMN insights.last_occurred_at IS 'When this insight pattern last appeared';

-- =====================================================
-- 3. TASK_INTERVENTIONS ENHANCEMENTS
-- =====================================================
-- Add XGBoost model output fields

ALTER TABLE task_interventions 
ADD COLUMN IF NOT EXISTS task_description TEXT;

ALTER TABLE task_interventions 
ADD COLUMN IF NOT EXISTS abandonment_probability NUMERIC(4,3);

ALTER TABLE task_interventions 
ADD COLUMN IF NOT EXISTS risk_level TEXT CHECK (risk_level IN ('LOW', 'MEDIUM', 'HIGH'));

ALTER TABLE task_interventions 
ADD COLUMN IF NOT EXISTS reasoning TEXT;

ALTER TABLE task_interventions 
ADD COLUMN IF NOT EXISTS triggered_at TIMESTAMPTZ DEFAULT NOW();

ALTER TABLE task_interventions 
ADD COLUMN IF NOT EXISTS task_complexity INTEGER CHECK (task_complexity BETWEEN 1 AND 10);

ALTER TABLE task_interventions 
ADD COLUMN IF NOT EXISTS minutes_since_start INTEGER;

ALTER TABLE task_interventions 
ADD COLUMN IF NOT EXISTS domain TEXT CHECK (domain IN ('BUSINESS', 'MICHAEL', 'FAMILY', 'PERSONAL'));

COMMENT ON COLUMN task_interventions.task_description IS 'What task triggered the intervention';
COMMENT ON COLUMN task_interventions.abandonment_probability IS 'XGBoost model prediction 0.000-1.000';
COMMENT ON COLUMN task_interventions.risk_level IS 'LOW (<40%), MEDIUM (40-70%), HIGH (>70%)';
COMMENT ON COLUMN task_interventions.reasoning IS 'Why this intervention was triggered';
COMMENT ON COLUMN task_interventions.task_complexity IS 'Task complexity 1-10 scale';
COMMENT ON COLUMN task_interventions.minutes_since_start IS 'How long task was active before intervention';
COMMENT ON COLUMN task_interventions.domain IS 'BUSINESS, MICHAEL, FAMILY, or PERSONAL';

-- =====================================================
-- 4. NEW TABLE: ABANDONMENT_PATTERNS
-- =====================================================
-- Track recurring abandonment patterns for ML training

CREATE TABLE IF NOT EXISTS abandonment_patterns (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL DEFAULT 1,
    pattern_type TEXT NOT NULL,
    description TEXT,
    triggers JSONB DEFAULT '[]',
    frequency INTEGER DEFAULT 1,
    avg_time_to_abandon INTEGER,
    successful_interventions INTEGER DEFAULT 0,
    failed_interventions INTEGER DEFAULT 0,
    last_occurred_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE abandonment_patterns IS 'Tracks recurring task abandonment patterns for ADHD ML model training';

-- =====================================================
-- 5. NEW TABLE: TASK_COMPLETION_STREAKS
-- =====================================================
-- Gamification for ADHD momentum

CREATE TABLE IF NOT EXISTS task_completion_streaks (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL DEFAULT 1,
    streak_type TEXT NOT NULL CHECK (streak_type IN ('DAILY', 'DOMAIN', 'NO_ABANDON')),
    domain TEXT,
    current_streak INTEGER DEFAULT 0,
    best_streak INTEGER DEFAULT 0,
    streak_start_date DATE,
    last_completion_date DATE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE task_completion_streaks IS 'Tracks completion streaks for ADHD momentum and gamification';

-- Create unique index for streak tracking
CREATE UNIQUE INDEX IF NOT EXISTS idx_streaks_user_type_domain 
ON task_completion_streaks(user_id, streak_type, COALESCE(domain, ''));

-- =====================================================
-- 6. INDEXES FOR PERFORMANCE
-- =====================================================

CREATE INDEX IF NOT EXISTS idx_daily_metrics_date ON daily_metrics(date);
CREATE INDEX IF NOT EXISTS idx_daily_metrics_user_date ON daily_metrics(user_id, date);
CREATE INDEX IF NOT EXISTS idx_task_interventions_triggered ON task_interventions(triggered_at);
CREATE INDEX IF NOT EXISTS idx_task_interventions_risk ON task_interventions(risk_level);
CREATE INDEX IF NOT EXISTS idx_insights_type ON insights(insight_type);
CREATE INDEX IF NOT EXISTS idx_abandonment_patterns_type ON abandonment_patterns(pattern_type);

-- =====================================================
-- 7. VIEWS FOR QUICK ANALYSIS
-- =====================================================

CREATE OR REPLACE VIEW v_adhd_daily_summary AS
SELECT 
    dm.date,
    dm.tasks_completed,
    dm.tasks_abandoned,
    dm.completion_rate,
    dm.context_switches,
    dm.domains,
    COALESCE(ti.intervention_count, 0) as interventions_triggered,
    dm.session_recommendation
FROM daily_metrics dm
LEFT JOIN (
    SELECT 
        DATE(triggered_at) as date,
        COUNT(*) as intervention_count
    FROM task_interventions
    GROUP BY DATE(triggered_at)
) ti ON dm.date = ti.date
WHERE dm.user_id = 1
ORDER BY dm.date DESC;

CREATE OR REPLACE VIEW v_intervention_effectiveness AS
SELECT 
    intervention_type,
    risk_level,
    COUNT(*) as total_interventions,
    SUM(CASE WHEN successful THEN 1 ELSE 0 END) as successful,
    ROUND(AVG(CASE WHEN successful THEN 1.0 ELSE 0.0 END) * 100, 1) as success_rate,
    ROUND(AVG(time_to_response), 1) as avg_response_minutes
FROM task_interventions
WHERE user_id = 1
GROUP BY intervention_type, risk_level
ORDER BY success_rate DESC;

-- =====================================================
-- 8. FUNCTION: LOG INTERVENTION
-- =====================================================

CREATE OR REPLACE FUNCTION log_adhd_intervention(
    p_task_description TEXT,
    p_intervention_type TEXT,
    p_abandonment_probability NUMERIC,
    p_risk_level TEXT,
    p_message TEXT,
    p_reasoning TEXT,
    p_task_complexity INTEGER DEFAULT 5,
    p_minutes_since_start INTEGER DEFAULT 0,
    p_domain TEXT DEFAULT 'BUSINESS'
) RETURNS INTEGER AS $$
DECLARE
    v_intervention_id INTEGER;
BEGIN
    INSERT INTO task_interventions (
        user_id,
        task_description,
        intervention_type,
        intervention_level,
        message,
        abandonment_probability,
        risk_level,
        reasoning,
        task_complexity,
        minutes_since_start,
        domain,
        triggered_at
    ) VALUES (
        1,
        p_task_description,
        p_intervention_type,
        CASE 
            WHEN p_minutes_since_start < 30 THEN 1
            WHEN p_minutes_since_start < 60 THEN 2
            ELSE 3
        END,
        p_message,
        p_abandonment_probability,
        p_risk_level,
        p_reasoning,
        p_task_complexity,
        p_minutes_since_start,
        p_domain,
        NOW()
    ) RETURNING id INTO v_intervention_id;
    
    RETURN v_intervention_id;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- MIGRATION COMPLETE
-- =====================================================
-- Run this entire script in Supabase SQL Editor
-- Then test with: SELECT * FROM v_adhd_daily_summary;
-- =====================================================
