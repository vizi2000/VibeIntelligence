-- Zenith Coder Database Initialization Script
-- This script sets up the initial database schema for Zenith Coder

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create custom types
CREATE TYPE project_status AS ENUM ('active', 'maintenance', 'archived', 'planning');
CREATE TYPE task_priority AS ENUM ('low', 'medium', 'high', 'critical');
CREATE TYPE task_status AS ENUM ('todo', 'in_progress', 'review', 'done', 'blocked');

-- Projects table
CREATE TABLE IF NOT EXISTS projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    status project_status DEFAULT 'planning',
    priority task_priority DEFAULT 'medium',
    health_score INTEGER DEFAULT 0 CHECK (health_score >= 0 AND health_score <= 100),
    docs_progress INTEGER DEFAULT 0 CHECK (docs_progress >= 0 AND docs_progress <= 100),
    github_url VARCHAR(500),
    local_path VARCHAR(500),
    tags TEXT[],
    revenue DECIMAL(10,2) DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_commit_at TIMESTAMP WITH TIME ZONE,
    next_task TEXT
);

-- Tasks table
CREATE TABLE IF NOT EXISTS tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    status task_status DEFAULT 'todo',
    priority task_priority DEFAULT 'medium',
    estimated_duration INTEGER, -- in minutes
    actual_duration INTEGER, -- in minutes
    tags TEXT[],
    assigned_to VARCHAR(255),
    due_date TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

-- AI Interactions table
CREATE TABLE IF NOT EXISTS ai_interactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID REFERENCES projects(id) ON DELETE SET NULL,
    task_id UUID REFERENCES tasks(id) ON DELETE SET NULL,
    interaction_type VARCHAR(100) NOT NULL, -- 'code_generation', 'documentation', 'analysis', etc.
    model_used VARCHAR(100) NOT NULL,
    prompt TEXT NOT NULL,
    response TEXT NOT NULL,
    tokens_used INTEGER,
    cost DECIMAL(8,4),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Monetization Opportunities table
CREATE TABLE IF NOT EXISTS monetization_opportunities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    opportunity_type VARCHAR(100) NOT NULL, -- 'saas', 'course', 'freelance', 'marketplace', etc.
    title VARCHAR(500) NOT NULL,
    description TEXT,
    potential_revenue VARCHAR(100),
    confidence_score INTEGER DEFAULT 0 CHECK (confidence_score >= 0 AND confidence_score <= 100),
    status VARCHAR(50) DEFAULT 'identified', -- 'identified', 'researching', 'implementing', 'active', 'completed'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Freelance Jobs table
CREATE TABLE IF NOT EXISTS freelance_jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(500) NOT NULL,
    description TEXT,
    platform VARCHAR(100), -- 'upwork', 'fiverr', 'freelancer', etc.
    job_url VARCHAR(1000),
    rate VARCHAR(100),
    rate_type VARCHAR(20), -- 'hourly', 'fixed', 'milestone'
    skills_required TEXT[],
    match_score INTEGER DEFAULT 0 CHECK (match_score >= 0 AND match_score <= 100),
    status VARCHAR(50) DEFAULT 'found', -- 'found', 'applied', 'interview', 'accepted', 'rejected', 'completed'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Knowledge Base Articles table
CREATE TABLE IF NOT EXISTS knowledge_articles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    source VARCHAR(200), -- 'ai_news', 'skool', 'documentation', etc.
    source_url VARCHAR(1000),
    tags TEXT[],
    relevance_score INTEGER DEFAULT 0 CHECK (relevance_score >= 0 AND relevance_score <= 100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User Settings table
CREATE TABLE IF NOT EXISTS user_settings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    setting_key VARCHAR(100) NOT NULL UNIQUE,
    setting_value JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status);
CREATE INDEX IF NOT EXISTS idx_projects_priority ON projects(priority);
CREATE INDEX IF NOT EXISTS idx_projects_updated_at ON projects(updated_at);
CREATE INDEX IF NOT EXISTS idx_projects_name_trgm ON projects USING gin (name gin_trgm_ops);

CREATE INDEX IF NOT EXISTS idx_tasks_project_id ON tasks(project_id);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_priority ON tasks(priority);
CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON tasks(due_date);

CREATE INDEX IF NOT EXISTS idx_ai_interactions_project_id ON ai_interactions(project_id);
CREATE INDEX IF NOT EXISTS idx_ai_interactions_created_at ON ai_interactions(created_at);
CREATE INDEX IF NOT EXISTS idx_ai_interactions_type ON ai_interactions(interaction_type);

CREATE INDEX IF NOT EXISTS idx_monetization_project_id ON monetization_opportunities(project_id);
CREATE INDEX IF NOT EXISTS idx_monetization_status ON monetization_opportunities(status);

CREATE INDEX IF NOT EXISTS idx_freelance_match_score ON freelance_jobs(match_score);
CREATE INDEX IF NOT EXISTS idx_freelance_status ON freelance_jobs(status);

CREATE INDEX IF NOT EXISTS idx_knowledge_tags ON knowledge_articles USING gin (tags);
CREATE INDEX IF NOT EXISTS idx_knowledge_title_trgm ON knowledge_articles USING gin (title gin_trgm_ops);

-- Create triggers for updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_projects_updated_at BEFORE UPDATE ON projects
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tasks_updated_at BEFORE UPDATE ON tasks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_monetization_updated_at BEFORE UPDATE ON monetization_opportunities
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_freelance_updated_at BEFORE UPDATE ON freelance_jobs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_knowledge_updated_at BEFORE UPDATE ON knowledge_articles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_settings_updated_at BEFORE UPDATE ON user_settings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert sample data for development
INSERT INTO projects (name, description, status, priority, health_score, docs_progress, tags, revenue, next_task) VALUES
('Zenith Coder', 'AI-powered development platform', 'active', 'high', 92, 85, ARRAY['Python', 'FastAPI', 'React', 'AI', 'MVP-Ready'], 0, 'Deploy MVP'),
('E-commerce API', 'RESTful API for online stores', 'active', 'high', 76, 45, ARRAY['Node.js', 'Express', 'MongoDB', 'Stripe', 'Production'], 1200, 'Security audit'),
('Personal Website', 'Portfolio and blog website', 'maintenance', 'low', 58, 20, ARRAY['React', 'Gatsby', 'GraphQL', 'Netlify'], 0, 'Update README');

INSERT INTO tasks (project_id, title, status, priority, estimated_duration) VALUES
((SELECT id FROM projects WHERE name = 'Zenith Coder'), 'Update README for API project', 'todo', 'high', 15),
((SELECT id FROM projects WHERE name = 'E-commerce API'), 'Fix authentication bug', 'in_progress', 'medium', 30),
((SELECT id FROM projects WHERE name = 'Personal Website'), 'Review PR #23', 'todo', 'low', 20);

INSERT INTO monetization_opportunities (project_id, opportunity_type, title, potential_revenue, confidence_score) VALUES
((SELECT id FROM projects WHERE name = 'E-commerce API'), 'saas', 'E-commerce API → SaaS', '$500/mo', 85),
((SELECT id FROM projects WHERE name = 'Zenith Coder'), 'course', 'Tutorial series → Course', '$1,200', 70),
((SELECT id FROM projects WHERE name = 'Personal Website'), 'marketplace', 'Code templates → Marketplace', 'TBD', 40);

INSERT INTO freelance_jobs (title, rate, rate_type, skills_required, match_score) VALUES
('Python API development', '$75/hr', 'hourly', ARRAY['Python', 'FastAPI', 'PostgreSQL'], 95),
('React dashboard', '$2,500', 'fixed', ARRAY['React', 'TypeScript', 'Tailwind'], 88);

INSERT INTO user_settings (setting_key, setting_value) VALUES
('default_ai_model', '{"code": "claude-3-5-sonnet", "analysis": "gpt-4o", "docs": "claude-3-5-sonnet"}'),
('pomodoro_duration', '{"work": 25, "break": 5, "long_break": 15}'),
('notification_preferences', '{"email": true, "push": false, "desktop": true}');

-- Create a view for project statistics
CREATE OR REPLACE VIEW project_stats AS
SELECT 
    p.id,
    p.name,
    p.status,
    p.health_score,
    p.docs_progress,
    COUNT(t.id) as total_tasks,
    COUNT(CASE WHEN t.status = 'done' THEN 1 END) as completed_tasks,
    COUNT(CASE WHEN t.status = 'todo' THEN 1 END) as pending_tasks,
    COUNT(mo.id) as monetization_opportunities,
    p.revenue,
    p.updated_at
FROM projects p
LEFT JOIN tasks t ON p.id = t.project_id
LEFT JOIN monetization_opportunities mo ON p.id = mo.project_id
GROUP BY p.id, p.name, p.status, p.health_score, p.docs_progress, p.revenue, p.updated_at;

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO zenith_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO zenith_user;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO zenith_user;

