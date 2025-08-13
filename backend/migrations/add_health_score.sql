-- Add health_score column to projects table
ALTER TABLE projects ADD COLUMN IF NOT EXISTS health_score INTEGER DEFAULT 0;

-- Update existing projects with calculated health scores based on available data
UPDATE projects SET health_score = 
  CASE 
    WHEN has_readme AND has_tests AND has_documentation THEN 90
    WHEN has_readme AND (has_tests OR has_documentation) THEN 75
    WHEN has_readme THEN 60
    WHEN has_tests THEN 50
    ELSE 40
  END
WHERE health_score IS NULL OR health_score = 0;