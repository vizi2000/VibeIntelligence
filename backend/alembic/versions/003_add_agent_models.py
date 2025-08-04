"""Add agent and developer models

Revision ID: 003
Revises: 002
Create Date: 2025-08-04 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade():
    # Create developer_profiles table
    op.create_table('developer_profiles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('full_name', sa.String(length=255), nullable=True),
        sa.Column('adhd_mode_enabled', sa.Boolean(), nullable=True),
        sa.Column('preferred_task_duration', sa.Integer(), nullable=True),
        sa.Column('break_reminder_interval', sa.Integer(), nullable=True),
        sa.Column('notification_preferences', sa.JSON(), nullable=True),
        sa.Column('primary_languages', sa.JSON(), nullable=True),
        sa.Column('frameworks', sa.JSON(), nullable=True),
        sa.Column('skill_levels', sa.JSON(), nullable=True),
        sa.Column('specializations', sa.JSON(), nullable=True),
        sa.Column('preferred_work_hours', sa.JSON(), nullable=True),
        sa.Column('productivity_patterns', sa.JSON(), nullable=True),
        sa.Column('focus_score', sa.Float(), nullable=True),
        sa.Column('vibe_score', sa.Integer(), nullable=True),
        sa.Column('eco_score', sa.Integer(), nullable=True),
        sa.Column('wellbeing_score', sa.Integer(), nullable=True),
        sa.Column('flow_state_percentage', sa.Float(), nullable=True),
        sa.Column('preferred_project_types', sa.JSON(), nullable=True),
        sa.Column('monetization_interests', sa.JSON(), nullable=True),
        sa.Column('preferred_ai_models', sa.JSON(), nullable=True),
        sa.Column('ai_personality_preference', sa.String(length=50), nullable=True),
        sa.Column('total_commits', sa.Integer(), nullable=True),
        sa.Column('total_projects', sa.Integer(), nullable=True),
        sa.Column('completed_tasks', sa.Integer(), nullable=True),
        sa.Column('streak_days', sa.Integer(), nullable=True),
        sa.Column('badges', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('last_active_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_developer_profiles_email'), 'developer_profiles', ['email'], unique=True)
    op.create_index(op.f('ix_developer_profiles_username'), 'developer_profiles', ['username'], unique=True)
    
    # Create developer_activities table
    op.create_table('developer_activities',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('developer_id', sa.Integer(), nullable=False),
        sa.Column('activity_type', sa.String(length=50), nullable=False),
        sa.Column('action', sa.String(length=255), nullable=False),
        sa.Column('target', sa.String(length=500), nullable=True),
        sa.Column('project_id', sa.Integer(), nullable=True),
        sa.Column('session_id', sa.String(length=100), nullable=True),
        sa.Column('details', sa.JSON(), nullable=True),
        sa.Column('prompt_used', sa.Text(), nullable=True),
        sa.Column('ai_response', sa.Text(), nullable=True),
        sa.Column('code_before', sa.Text(), nullable=True),
        sa.Column('code_after', sa.Text(), nullable=True),
        sa.Column('duration_seconds', sa.Integer(), nullable=True),
        sa.Column('lines_changed', sa.Integer(), nullable=True),
        sa.Column('complexity_score', sa.Float(), nullable=True),
        sa.Column('focus_score', sa.Float(), nullable=True),
        sa.Column('ai_provider', sa.String(length=50), nullable=True),
        sa.Column('ai_model', sa.String(length=100), nullable=True),
        sa.Column('tokens_used', sa.Integer(), nullable=True),
        sa.Column('ai_cost', sa.Float(), nullable=True),
        sa.Column('vibe_impact', sa.Integer(), nullable=True),
        sa.Column('eco_impact', sa.Integer(), nullable=True),
        sa.Column('learning_value', sa.Integer(), nullable=True),
        sa.Column('success', sa.Boolean(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['developer_id'], ['developer_profiles.id'], ),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_developer_activities_activity_type'), 'developer_activities', ['activity_type'], unique=False)
    op.create_index(op.f('ix_developer_activities_session_id'), 'developer_activities', ['session_id'], unique=False)
    
    # Create activity_summaries table
    op.create_table('activity_summaries',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('developer_id', sa.Integer(), nullable=False),
        sa.Column('date', sa.DateTime(), nullable=False),
        sa.Column('total_activities', sa.Integer(), nullable=True),
        sa.Column('total_duration_seconds', sa.Integer(), nullable=True),
        sa.Column('total_lines_changed', sa.Integer(), nullable=True),
        sa.Column('total_commits', sa.Integer(), nullable=True),
        sa.Column('total_ai_tokens', sa.Integer(), nullable=True),
        sa.Column('total_ai_cost', sa.Float(), nullable=True),
        sa.Column('activity_breakdown', sa.JSON(), nullable=True),
        sa.Column('language_breakdown', sa.JSON(), nullable=True),
        sa.Column('average_focus_score', sa.Float(), nullable=True),
        sa.Column('peak_productivity_hour', sa.Integer(), nullable=True),
        sa.Column('flow_state_minutes', sa.Integer(), nullable=True),
        sa.Column('daily_vibe_score', sa.Integer(), nullable=True),
        sa.Column('daily_eco_score', sa.Integer(), nullable=True),
        sa.Column('daily_learning_score', sa.Integer(), nullable=True),
        sa.Column('key_achievements', sa.JSON(), nullable=True),
        sa.Column('main_projects', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['developer_id'], ['developer_profiles.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_activity_summaries_date'), 'activity_summaries', ['date'], unique=False)
    
    # Create agent_tasks table
    op.create_table('agent_tasks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('developer_id', sa.Integer(), nullable=False),
        sa.Column('agent_type', sa.String(length=50), nullable=False),
        sa.Column('task_name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('priority', sa.String(length=20), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('scheduled_at', sa.DateTime(), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('next_run_at', sa.DateTime(), nullable=True),
        sa.Column('is_recurring', sa.Boolean(), nullable=True),
        sa.Column('recurrence_pattern', sa.JSON(), nullable=True),
        sa.Column('max_retries', sa.Integer(), nullable=True),
        sa.Column('retry_count', sa.Integer(), nullable=True),
        sa.Column('input_data', sa.JSON(), nullable=True),
        sa.Column('output_data', sa.JSON(), nullable=True),
        sa.Column('context', sa.JSON(), nullable=True),
        sa.Column('execution_time_seconds', sa.Float(), nullable=True),
        sa.Column('ai_provider', sa.String(length=50), nullable=True),
        sa.Column('ai_model', sa.String(length=100), nullable=True),
        sa.Column('tokens_used', sa.Integer(), nullable=True),
        sa.Column('cost', sa.Float(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('error_details', sa.JSON(), nullable=True),
        sa.Column('impact_score', sa.Integer(), nullable=True),
        sa.Column('automation_score', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['developer_id'], ['developer_profiles.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_agent_tasks_agent_type'), 'agent_tasks', ['agent_type'], unique=False)
    op.create_index(op.f('ix_agent_tasks_status'), 'agent_tasks', ['status'], unique=False)
    
    # Create agent_subtasks table
    op.create_table('agent_subtasks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('parent_task_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('sequence_order', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('input_data', sa.JSON(), nullable=True),
        sa.Column('output_data', sa.JSON(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['parent_task_id'], ['agent_tasks.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create agent_schedules table
    op.create_table('agent_schedules',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('developer_id', sa.Integer(), nullable=False),
        sa.Column('agent_type', sa.String(length=50), nullable=False),
        sa.Column('enabled', sa.Boolean(), nullable=True),
        sa.Column('schedule_pattern', sa.JSON(), nullable=True),
        sa.Column('preferred_hours', sa.JSON(), nullable=True),
        sa.Column('blackout_periods', sa.JSON(), nullable=True),
        sa.Column('max_daily_runs', sa.Integer(), nullable=True),
        sa.Column('max_tokens_per_run', sa.Integer(), nullable=True),
        sa.Column('max_cost_per_day', sa.Float(), nullable=True),
        sa.Column('daily_runs_count', sa.Integer(), nullable=True),
        sa.Column('daily_tokens_used', sa.Integer(), nullable=True),
        sa.Column('daily_cost_used', sa.Float(), nullable=True),
        sa.Column('last_reset_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['developer_id'], ['developer_profiles.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create skill_progress table
    op.create_table('skill_progress',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('developer_id', sa.Integer(), nullable=False),
        sa.Column('skill_name', sa.String(length=100), nullable=False),
        sa.Column('skill_category', sa.String(length=50), nullable=True),
        sa.Column('current_level', sa.Integer(), nullable=True),
        sa.Column('previous_level', sa.Integer(), nullable=True),
        sa.Column('level_change', sa.Integer(), nullable=True),
        sa.Column('practice_hours', sa.Float(), nullable=True),
        sa.Column('lines_written', sa.Integer(), nullable=True),
        sa.Column('projects_used_in', sa.Integer(), nullable=True),
        sa.Column('errors_encountered', sa.Integer(), nullable=True),
        sa.Column('errors_resolved', sa.Integer(), nullable=True),
        sa.Column('code_quality_score', sa.Float(), nullable=True),
        sa.Column('best_practices_score', sa.Float(), nullable=True),
        sa.Column('innovation_score', sa.Float(), nullable=True),
        sa.Column('learning_sources', sa.JSON(), nullable=True),
        sa.Column('ai_interactions', sa.Integer(), nullable=True),
        sa.Column('milestones_achieved', sa.JSON(), nullable=True),
        sa.Column('next_milestone', sa.JSON(), nullable=True),
        sa.Column('code_samples', sa.JSON(), nullable=True),
        sa.Column('assessment_notes', sa.Text(), nullable=True),
        sa.Column('first_used_at', sa.DateTime(), nullable=True),
        sa.Column('last_used_at', sa.DateTime(), nullable=True),
        sa.Column('assessed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['developer_id'], ['developer_profiles.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_skill_progress_skill_name'), 'skill_progress', ['skill_name'], unique=False)
    
    # Create skill_recommendations table
    op.create_table('skill_recommendations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('developer_id', sa.Integer(), nullable=False),
        sa.Column('skill_name', sa.String(length=100), nullable=False),
        sa.Column('recommendation_type', sa.String(length=50), nullable=True),
        sa.Column('priority', sa.String(length=20), nullable=True),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('market_demand', sa.Integer(), nullable=True),
        sa.Column('synergy_score', sa.Integer(), nullable=True),
        sa.Column('suggested_resources', sa.JSON(), nullable=True),
        sa.Column('estimated_hours', sa.Integer(), nullable=True),
        sa.Column('prerequisite_skills', sa.JSON(), nullable=True),
        sa.Column('career_impact', sa.JSON(), nullable=True),
        sa.Column('project_applications', sa.JSON(), nullable=True),
        sa.Column('monetization_potential', sa.Integer(), nullable=True),
        sa.Column('accepted', sa.String(), nullable=True),
        sa.Column('started_learning', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['developer_id'], ['developer_profiles.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    # Drop tables in reverse order
    op.drop_table('skill_recommendations')
    op.drop_table('skill_progress')
    op.drop_table('agent_schedules')
    op.drop_table('agent_subtasks')
    op.drop_table('agent_tasks')
    op.drop_table('activity_summaries')
    op.drop_table('developer_activities')
    op.drop_table('developer_profiles')