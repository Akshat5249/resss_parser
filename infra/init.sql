-- Create UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table: Stores basic user information
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email TEXT UNIQUE NOT NULL,
    full_name TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Resume jobs table: Tracks resume processing tasks and stores extracted data
CREATE TABLE IF NOT EXISTS resume_jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    original_filename TEXT NOT NULL,
    file_url TEXT,
    raw_text TEXT,
    parsed_data JSONB,
    status TEXT NOT NULL CHECK (status IN ('pending', 'processing', 'done', 'failed')) DEFAULT 'pending',
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- JD jobs table: Tracks job description processing tasks and stores extracted data
CREATE TABLE IF NOT EXISTS jd_jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    raw_text TEXT NOT NULL,
    parsed_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Analysis results table: Stores the detailed scoring and feedback for a resume against a JD
CREATE TABLE IF NOT EXISTS analysis_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    resume_job_id UUID NOT NULL REFERENCES resume_jobs(id) ON DELETE CASCADE,
    jd_job_id UUID REFERENCES jd_jobs(id) ON DELETE CASCADE, -- NULL means baseline mode
    score_total INTEGER NOT NULL CHECK (score_total >= 0 AND score_total <= 100),
    score_breakdown JSONB NOT NULL, -- {skill_match, experience, projects, education, formatting}
    gaps JSONB NOT NULL, -- {missing_skills: [], weak_bullets: []}
    enhancements JSONB, -- list of rewritten bullets
    compliance_issues JSONB,
    feedback_text TEXT,
    learning_path JSONB,
    pdf_report_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Ranking sessions table: Groups multiple resumes for comparison against a JD
CREATE TABLE IF NOT EXISTS ranking_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    jd_job_id UUID NOT NULL REFERENCES jd_jobs(id) ON DELETE CASCADE,
    resume_job_ids UUID[] NOT NULL,
    ranked_results JSONB NOT NULL, -- ordered list with scores
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_resume_jobs_user_id ON resume_jobs(user_id);
CREATE INDEX IF NOT EXISTS idx_resume_jobs_status ON resume_jobs(status);
CREATE INDEX IF NOT EXISTS idx_analysis_results_resume_job_id ON analysis_results(resume_job_id);
CREATE INDEX IF NOT EXISTS idx_analysis_results_jd_job_id ON analysis_results(jd_job_id);

-- Trigger for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();
CREATE TRIGGER update_resume_jobs_updated_at BEFORE UPDATE ON resume_jobs FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();
CREATE TRIGGER update_jd_jobs_updated_at BEFORE UPDATE ON jd_jobs FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();
CREATE TRIGGER update_analysis_results_updated_at BEFORE UPDATE ON analysis_results FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();
CREATE TRIGGER update_ranking_sessions_updated_at BEFORE UPDATE ON ranking_sessions FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();
