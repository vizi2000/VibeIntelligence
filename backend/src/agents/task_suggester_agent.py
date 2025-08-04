"""
Task Suggester Agent
AI-powered task suggestions based on developer patterns
Following vibecoding principles for ADHD-friendly task management
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func

from .base_agent import BaseAgent
from ..models.agent_task import AgentTask, AgentType
from ..models.developer_profile import DeveloperProfile
from ..models.developer_activity import DeveloperActivity, ActivitySummary
from ..models.project import Project
from ..ai.orchestrator import TaskType

logger = logging.getLogger(__name__)


class TaskSuggesterAgent(BaseAgent):
    """
    Agent that suggests tasks based on:
    - Developer work patterns
    - Project needs
    - Skill development goals
    - ADHD-friendly task sizing
    """
    
    def __init__(self):
        super().__init__(AgentType.TASK_SUGGESTER, "Task Suggester")
        self.task_categories = [
            "quick_wins",
            "skill_building",
            "maintenance",
            "creative",
            "documentation",
            "refactoring"
        ]
    
    async def execute_task(self, task: AgentTask, db: Session) -> Dict[str, Any]:
        """Execute task suggestion analysis"""
        suggestion_type = task.input_data.get("suggestion_type", "daily")
        
        if suggestion_type == "daily":
            return await self._suggest_daily_tasks(task, db)
        elif suggestion_type == "weekly":
            return await self._suggest_weekly_plan(task, db)
        elif suggestion_type == "skill_based":
            return await self._suggest_skill_tasks(task, db)
        elif suggestion_type == "project_based":
            return await self._suggest_project_tasks(task, db)
        elif suggestion_type == "break_task":
            return await self._break_down_task(task, db)
        else:
            return await self._general_suggestions(task, db)
    
    async def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze task suggestion needs"""
        developer_state = context.get("developer_state", {})
        current_time = datetime.utcnow()
        
        analysis = {
            "suggestions_needed": True,
            "suggestion_types": [],
            "priority_level": "medium",
            "adhd_considerations": []
        }
        
        # Check developer's current state
        if developer_state.get("focus_score", 0) < 50:
            analysis["suggestion_types"].append("quick_wins")
            analysis["adhd_considerations"].append("Low focus - suggest easy tasks")
        
        # Time-based suggestions
        hour = current_time.hour
        if 9 <= hour <= 11:  # Morning peak
            analysis["suggestion_types"].append("creative")
            analysis["priority_level"] = "high"
        elif 14 <= hour <= 16:  # Afternoon slump
            analysis["suggestion_types"].append("maintenance")
            analysis["adhd_considerations"].append("Post-lunch - suggest routine tasks")
        
        return analysis
    
    async def _suggest_daily_tasks(self, task: AgentTask, db: Session) -> Dict[str, Any]:
        """Suggest tasks for the day"""
        developer_id = task.developer_id
        developer = db.query(DeveloperProfile).filter(
            DeveloperProfile.id == developer_id
        ).first()
        
        if not developer:
            raise ValueError(f"Developer {developer_id} not found")
        
        logger.info(f"📋 Generating daily tasks for {developer.username}")
        
        # Get recent activities to understand patterns
        recent_activities = db.query(DeveloperActivity).filter(
            DeveloperActivity.developer_id == developer_id,
            DeveloperActivity.created_at >= datetime.utcnow() - timedelta(days=7)
        ).order_by(DeveloperActivity.created_at.desc()).limit(50).all()
        
        # Get active projects
        active_projects = db.query(Project).filter(
            Project.is_active == True
        ).limit(5).all()
        
        # Analyze patterns
        activity_summary = self._analyze_activity_patterns(recent_activities)
        
        # Generate task suggestions with AI
        prompt = f"""
        Generate daily task suggestions for a developer with ADHD:
        
        Developer Profile:
        - Preferred task duration: {developer.preferred_task_duration} minutes
        - Primary languages: {developer.primary_languages}
        - Current vibe score: {developer.vibe_score}/100
        - Focus score: {developer.focus_score}/100
        
        Recent Activity Patterns:
        - Most productive hours: {activity_summary.get('productive_hours')}
        - Average task completion time: {activity_summary.get('avg_completion_time')}
        - Preferred task types: {activity_summary.get('preferred_types')}
        
        Active Projects: {[p.name for p in active_projects]}
        
        Generate 6-8 tasks that are:
        1. ADHD-friendly (15-45 minute chunks)
        2. Mix of different types (coding, planning, breaks)
        3. Aligned with peak productivity times
        4. Include quick wins for momentum
        5. Balance challenge and achievability
        
        Format each task with:
        - Title
        - Duration (minutes)
        - Type (coding/planning/review/break)
        - Energy level required (low/medium/high)
        - Why this task now (motivation)
        """
        
        ai_response = await self.use_ai(prompt, TaskType.GENERAL_CHAT)
        suggested_tasks = self._parse_task_suggestions(ai_response.get("content", ""))
        
        # Add metadata to suggestions
        for i, suggested_task in enumerate(suggested_tasks):
            suggested_task["priority"] = self._calculate_task_priority(
                suggested_task, 
                developer, 
                activity_summary
            )
            suggested_task["adhd_score"] = self._calculate_adhd_friendliness(suggested_task)
        
        # Sort by optimal order
        suggested_tasks = self._optimize_task_order(suggested_tasks, developer)
        
        # Log activity
        await self.log_activity(
            developer_id,
            f"Generated {len(suggested_tasks)} daily task suggestions",
            None,
            {"task_count": len(suggested_tasks)}
        )
        
        return {
            "developer_id": developer_id,
            "suggestion_type": "daily",
            "tasks": suggested_tasks,
            "total_estimated_time": sum(t.get("duration", 30) for t in suggested_tasks),
            "motivational_message": self._get_motivational_message(developer),
            "productivity_tips": self._get_productivity_tips(activity_summary)
        }
    
    async def _suggest_weekly_plan(self, task: AgentTask, db: Session) -> Dict[str, Any]:
        """Suggest weekly task plan"""
        developer_id = task.developer_id
        
        # Get developer's goals and patterns
        developer = db.query(DeveloperProfile).filter(
            DeveloperProfile.id == developer_id
        ).first()
        
        # Generate weekly structure
        prompt = f"""
        Create a weekly task plan for a developer:
        
        Goals:
        - Skill development in: {developer.primary_languages}
        - Project progress on active projects
        - Maintain work-life balance
        - ADHD-friendly structure
        
        Create a 5-day plan with:
        1. Theme for each day (e.g., "Feature Friday", "Maintenance Monday")
        2. 4-6 key tasks per day
        3. Built-in breaks and variety
        4. Progressive difficulty through the week
        5. Friday afternoon for easy/fun tasks
        
        Include time for:
        - Deep work sessions
        - Code reviews
        - Learning/skill development
        - Documentation
        - Planning for next week
        """
        
        ai_response = await self.use_ai(prompt, TaskType.GENERAL_CHAT)
        weekly_plan = self._parse_weekly_plan(ai_response.get("content", ""))
        
        return {
            "developer_id": developer_id,
            "suggestion_type": "weekly",
            "weekly_plan": weekly_plan,
            "total_tasks": sum(len(day.get("tasks", [])) for day in weekly_plan),
            "themes": [day.get("theme") for day in weekly_plan],
            "flexibility_notes": "This plan is flexible - adjust based on daily energy levels"
        }
    
    async def _suggest_skill_tasks(self, task: AgentTask, db: Session) -> Dict[str, Any]:
        """Suggest tasks for skill development"""
        developer_id = task.developer_id
        target_skill = task.input_data.get("target_skill")
        
        developer = db.query(DeveloperProfile).filter(
            DeveloperProfile.id == developer_id
        ).first()
        
        current_level = developer.skill_levels.get(target_skill, 0)
        
        prompt = f"""
        Create skill development tasks for learning {target_skill}:
        
        Current level: {current_level}/100
        Learning style: ADHD-friendly, hands-on
        
        Suggest 5-7 progressive tasks that:
        1. Start with quick wins (10-15 min tasks)
        2. Build complexity gradually
        3. Include practical exercises
        4. Have clear, measurable outcomes
        5. Mix theory and practice
        
        Each task should specify:
        - What to build/learn
        - Resources needed
        - Success criteria
        - Skill points gained
        """
        
        ai_response = await self.use_ai(prompt, TaskType.GENERAL_CHAT)
        skill_tasks = self._parse_skill_tasks(ai_response.get("content", ""))
        
        return {
            "developer_id": developer_id,
            "suggestion_type": "skill_based",
            "target_skill": target_skill,
            "current_level": current_level,
            "tasks": skill_tasks,
            "estimated_level_gain": 10,
            "learning_path": self._create_learning_path(target_skill, current_level)
        }
    
    async def _suggest_project_tasks(self, task: AgentTask, db: Session) -> Dict[str, Any]:
        """Suggest tasks for specific project"""
        project_id = task.input_data.get("project_id")
        project = db.query(Project).filter(Project.id == project_id).first()
        
        if not project:
            raise ValueError(f"Project {project_id} not found")
        
        # Analyze project needs
        project_analysis = {
            "has_tests": project.has_tests,
            "has_docs": project.has_documentation,
            "tech_stack": project.tech_stack
        }
        
        prompt = f"""
        Suggest next tasks for project: {project.name}
        
        Project state:
        - Has tests: {project.has_tests}
        - Has documentation: {project.has_documentation}
        - Tech stack: {project.tech_stack}
        
        Suggest 5-8 tasks that:
        1. Address missing components
        2. Improve code quality
        3. Add user value
        4. Are completable in 30-60 minutes each
        5. Follow best practices
        
        Prioritize based on:
        - Impact on project health
        - User value
        - Technical debt reduction
        """
        
        ai_response = await self.use_ai(prompt, TaskType.GENERAL_CHAT)
        project_tasks = self._parse_project_tasks(ai_response.get("content", ""))
        
        return {
            "project_id": project_id,
            "project_name": project.name,
            "suggestion_type": "project_based",
            "tasks": project_tasks,
            "project_health_impact": self._calculate_health_impact(project_tasks, project_analysis)
        }
    
    async def _break_down_task(self, task: AgentTask, db: Session) -> Dict[str, Any]:
        """Break down large task into ADHD-friendly subtasks"""
        large_task = task.input_data.get("task_description")
        estimated_hours = task.input_data.get("estimated_hours", 4)
        
        prompt = f"""
        Break down this large task for someone with ADHD:
        
        Task: {large_task}
        Estimated time: {estimated_hours} hours
        
        Create subtasks that are:
        1. 15-45 minutes each
        2. Clearly defined with specific outcomes
        3. Ordered logically with dependencies
        4. Include breaks between intense tasks
        5. Have clear success criteria
        
        Format:
        - Subtask name
        - Duration
        - Prerequisites
        - Success criteria
        - Energy level needed
        """
        
        ai_response = await self.use_ai(prompt, TaskType.GENERAL_CHAT)
        subtasks = self._parse_subtasks(ai_response.get("content", ""))
        
        # Add ordering and dependencies
        subtasks = self._add_task_dependencies(subtasks)
        
        return {
            "original_task": large_task,
            "estimated_hours": estimated_hours,
            "subtasks": subtasks,
            "total_subtasks": len(subtasks),
            "includes_breaks": self._count_breaks(subtasks),
            "execution_plan": self._create_execution_plan(subtasks)
        }
    
    async def _general_suggestions(self, task: AgentTask, db: Session) -> Dict[str, Any]:
        """Provide general task suggestions"""
        developer_id = task.developer_id
        
        # Get developer context
        developer = db.query(DeveloperProfile).filter(
            DeveloperProfile.id == developer_id
        ).first()
        
        # Mix of different task types
        suggestions = {
            "quick_wins": await self._get_quick_wins(developer, db),
            "learning_tasks": await self._get_learning_tasks(developer, db),
            "maintenance_tasks": await self._get_maintenance_tasks(developer, db),
            "creative_tasks": await self._get_creative_tasks(developer, db)
        }
        
        return {
            "developer_id": developer_id,
            "suggestion_type": "general",
            "suggestions": suggestions,
            "recommendation": self._get_task_recommendation(developer, suggestions)
        }
    
    def _analyze_activity_patterns(self, activities: List[DeveloperActivity]) -> Dict[str, Any]:
        """Analyze developer activity patterns"""
        patterns = {
            "productive_hours": [],
            "avg_completion_time": 30,
            "preferred_types": [],
            "success_rate": 0
        }
        
        if not activities:
            return patterns
        
        # Analyze productivity by hour
        hour_productivity = {}
        for activity in activities:
            if activity.started_at:
                hour = activity.started_at.hour
                if hour not in hour_productivity:
                    hour_productivity[hour] = []
                hour_productivity[hour].append(activity.focus_score or 50)
        
        # Find most productive hours
        productive_hours = sorted(
            hour_productivity.items(),
            key=lambda x: sum(x[1]) / len(x[1]) if x[1] else 0,
            reverse=True
        )[:3]
        patterns["productive_hours"] = [h[0] for h in productive_hours]
        
        # Calculate average completion time
        completion_times = [
            a.duration_seconds for a in activities 
            if a.duration_seconds and a.duration_seconds < 7200  # Less than 2 hours
        ]
        if completion_times:
            patterns["avg_completion_time"] = sum(completion_times) // len(completion_times) // 60
        
        # Success rate
        successful = sum(1 for a in activities if a.success)
        patterns["success_rate"] = (successful / len(activities)) * 100 if activities else 0
        
        return patterns
    
    def _parse_task_suggestions(self, ai_response: str) -> List[Dict[str, Any]]:
        """Parse AI task suggestions"""
        tasks = []
        current_task = {}
        
        lines = ai_response.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                if current_task:
                    tasks.append(current_task)
                    current_task = {}
                continue
            
            # Parse task attributes
            if line.startswith('-') or line.startswith('•'):
                if current_task:
                    tasks.append(current_task)
                current_task = {"title": line[1:].strip()}
            elif "duration:" in line.lower() or "minutes" in line.lower():
                # Extract duration
                import re
                duration_match = re.search(r'(\d+)\s*min', line.lower())
                if duration_match:
                    current_task["duration"] = int(duration_match.group(1))
            elif "type:" in line.lower():
                current_task["type"] = line.split(':', 1)[1].strip()
            elif "energy:" in line.lower():
                current_task["energy_level"] = line.split(':', 1)[1].strip()
        
        if current_task:
            tasks.append(current_task)
        
        # Ensure all tasks have required fields
        for task in tasks:
            task.setdefault("duration", 30)
            task.setdefault("type", "general")
            task.setdefault("energy_level", "medium")
        
        return tasks
    
    def _calculate_task_priority(self, task: Dict, developer: DeveloperProfile, patterns: Dict) -> int:
        """Calculate task priority score"""
        priority = 50  # Base priority
        
        # Boost quick wins
        if task.get("duration", 30) <= 20:
            priority += 20
        
        # Align with productive hours
        current_hour = datetime.utcnow().hour
        if current_hour in patterns.get("productive_hours", []):
            priority += 15
        
        # Match energy levels
        if developer.focus_score > 70 and task.get("energy_level") == "high":
            priority += 10
        elif developer.focus_score < 50 and task.get("energy_level") == "low":
            priority += 10
        
        return min(100, priority)
    
    def _calculate_adhd_friendliness(self, task: Dict) -> int:
        """Calculate how ADHD-friendly a task is"""
        score = 50
        
        # Duration scoring
        duration = task.get("duration", 30)
        if 15 <= duration <= 30:
            score += 30
        elif 30 < duration <= 45:
            score += 20
        elif duration > 60:
            score -= 20
        
        # Clear definition
        if task.get("title") and len(task["title"]) > 10:
            score += 10
        
        # Type variety
        if task.get("type") in ["break", "creative", "review"]:
            score += 10
        
        return min(100, score)
    
    def _optimize_task_order(self, tasks: List[Dict], developer: DeveloperProfile) -> List[Dict]:
        """Optimize task order for ADHD flow"""
        if not tasks:
            return tasks
        
        # Start with a quick win
        quick_wins = [t for t in tasks if t.get("duration", 30) <= 20]
        other_tasks = [t for t in tasks if t.get("duration", 30) > 20]
        
        optimized = []
        
        # Add a quick win first
        if quick_wins:
            optimized.append(quick_wins.pop(0))
        
        # Alternate between different types
        last_type = optimized[0].get("type") if optimized else None
        
        remaining = quick_wins + other_tasks
        while remaining:
            # Find task with different type
            different_type = None
            for i, task in enumerate(remaining):
                if task.get("type") != last_type:
                    different_type = remaining.pop(i)
                    break
            
            if different_type:
                optimized.append(different_type)
                last_type = different_type.get("type")
            else:
                optimized.append(remaining.pop(0))
        
        return optimized
    
    def _get_motivational_message(self, developer: DeveloperProfile) -> str:
        """Get personalized motivational message"""
        messages = [
            f"You've completed {developer.completed_tasks} tasks! Keep the momentum going! 🚀",
            f"Your vibe score is {developer.vibe_score}/100. Let's boost it with some wins today! ✨",
            f"Remember: Progress over perfection. You've got this! 💪",
            f"Small steps lead to big changes. Start with just one task! 🎯",
            f"Your streak is {developer.streak_days} days! Let's add another! 🔥"
        ]
        
        import random
        return random.choice(messages)
    
    def _get_productivity_tips(self, patterns: Dict) -> List[str]:
        """Get productivity tips based on patterns"""
        tips = []
        
        if patterns.get("productive_hours"):
            hours = patterns["productive_hours"]
            tips.append(f"Your peak hours are around {hours[0]}:00. Schedule important tasks then!")
        
        if patterns.get("avg_completion_time", 30) > 45:
            tips.append("Try breaking tasks into smaller 20-30 minute chunks")
        
        if patterns.get("success_rate", 0) < 70:
            tips.append("Consider starting with easier tasks to build momentum")
        
        tips.append("Remember to take breaks - they boost productivity!")
        
        return tips
    
    def _parse_weekly_plan(self, ai_response: str) -> List[Dict[str, Any]]:
        """Parse weekly plan from AI response"""
        days = []
        current_day = {}
        
        lines = ai_response.split('\n')
        for line in lines:
            if any(day in line.lower() for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']):
                if current_day:
                    days.append(current_day)
                current_day = {
                    "day": line.strip(),
                    "theme": "",
                    "tasks": []
                }
            elif "theme:" in line.lower():
                current_day["theme"] = line.split(':', 1)[1].strip()
            elif line.strip().startswith(('-', '•', '1.', '2.', '3.')):
                if current_day:
                    current_day["tasks"].append(line.strip())
        
        if current_day:
            days.append(current_day)
        
        return days
    
    def _parse_skill_tasks(self, ai_response: str) -> List[Dict[str, Any]]:
        """Parse skill development tasks"""
        tasks = []
        current_task = {}
        
        for line in ai_response.split('\n'):
            line = line.strip()
            if not line:
                if current_task:
                    tasks.append(current_task)
                    current_task = {}
                continue
            
            if line.startswith(('-', '•')) or any(f"{i}." in line for i in range(1, 10)):
                if current_task:
                    tasks.append(current_task)
                current_task = {"title": line.lstrip('-•0123456789. ')}
            elif "resource" in line.lower():
                current_task["resources"] = line.split(':', 1)[1].strip()
            elif "success" in line.lower() or "criteria" in line.lower():
                current_task["success_criteria"] = line.split(':', 1)[1].strip()
            elif "skill points" in line.lower():
                import re
                points = re.search(r'(\d+)', line)
                if points:
                    current_task["skill_points"] = int(points.group(1))
        
        if current_task:
            tasks.append(current_task)
        
        return tasks
    
    def _create_learning_path(self, skill: str, current_level: int) -> List[Dict[str, Any]]:
        """Create learning path for skill"""
        milestones = []
        
        levels = [
            (10, "Beginner", "Basic syntax and concepts"),
            (30, "Novice", "Simple projects and exercises"),
            (50, "Intermediate", "Real-world applications"),
            (70, "Advanced", "Complex patterns and optimization"),
            (90, "Expert", "Teaching and contributing")
        ]
        
        for level, title, description in levels:
            if level > current_level:
                milestones.append({
                    "level": level,
                    "title": f"{skill} - {title}",
                    "description": description,
                    "estimated_hours": (level - current_level) * 2
                })
        
        return milestones
    
    def _parse_project_tasks(self, ai_response: str) -> List[Dict[str, Any]]:
        """Parse project-specific tasks"""
        return self._parse_task_suggestions(ai_response)  # Reuse general parser
    
    def _calculate_health_impact(self, tasks: List[Dict], project_state: Dict) -> Dict[str, int]:
        """Calculate impact on project health"""
        impact = {
            "documentation": 0,
            "testing": 0,
            "code_quality": 0,
            "features": 0
        }
        
        for task in tasks:
            title_lower = task.get("title", "").lower()
            if "doc" in title_lower or "readme" in title_lower:
                impact["documentation"] += 10
            elif "test" in title_lower:
                impact["testing"] += 10
            elif "refactor" in title_lower or "clean" in title_lower:
                impact["code_quality"] += 10
            elif "feature" in title_lower or "implement" in title_lower:
                impact["features"] += 10
        
        return impact
    
    def _parse_subtasks(self, ai_response: str) -> List[Dict[str, Any]]:
        """Parse subtasks from breakdown"""
        return self._parse_task_suggestions(ai_response)  # Reuse general parser
    
    def _add_task_dependencies(self, subtasks: List[Dict]) -> List[Dict]:
        """Add dependencies between subtasks"""
        for i, task in enumerate(subtasks):
            task["id"] = i + 1
            task["dependencies"] = [i] if i > 0 else []
        return subtasks
    
    def _count_breaks(self, subtasks: List[Dict]) -> int:
        """Count break tasks"""
        return sum(1 for task in subtasks if "break" in task.get("type", "").lower())
    
    def _create_execution_plan(self, subtasks: List[Dict]) -> str:
        """Create execution plan summary"""
        total_time = sum(task.get("duration", 30) for task in subtasks)
        break_count = self._count_breaks(subtasks)
        
        return (f"Total time: {total_time // 60}h {total_time % 60}m | "
                f"Tasks: {len(subtasks)} | Breaks: {break_count}")
    
    async def _get_quick_wins(self, developer: DeveloperProfile, db: Session) -> List[Dict]:
        """Get quick win tasks"""
        return [
            {"title": "Update project README", "duration": 15, "impact": "high"},
            {"title": "Fix a simple bug", "duration": 20, "impact": "medium"},
            {"title": "Add code comments", "duration": 10, "impact": "low"},
            {"title": "Organize imports", "duration": 5, "impact": "low"}
        ]
    
    async def _get_learning_tasks(self, developer: DeveloperProfile, db: Session) -> List[Dict]:
        """Get learning tasks"""
        return [
            {"title": "Watch a 10-min tutorial", "duration": 10, "skill": "varies"},
            {"title": "Read documentation for 15 min", "duration": 15, "skill": "varies"},
            {"title": "Try a new coding pattern", "duration": 30, "skill": "varies"}
        ]
    
    async def _get_maintenance_tasks(self, developer: DeveloperProfile, db: Session) -> List[Dict]:
        """Get maintenance tasks"""
        return [
            {"title": "Run and fix linting errors", "duration": 20},
            {"title": "Update dependencies", "duration": 15},
            {"title": "Clean up unused code", "duration": 25}
        ]
    
    async def _get_creative_tasks(self, developer: DeveloperProfile, db: Session) -> List[Dict]:
        """Get creative tasks"""
        return [
            {"title": "Brainstorm new feature ideas", "duration": 20},
            {"title": "Design a better UI component", "duration": 30},
            {"title": "Experiment with new library", "duration": 45}
        ]
    
    def _get_task_recommendation(self, developer: DeveloperProfile, suggestions: Dict) -> str:
        """Get personalized task recommendation"""
        if developer.focus_score > 70:
            return "High focus detected! Tackle a creative or complex task."
        elif developer.focus_score < 30:
            return "Low energy? Start with a quick win to build momentum!"
        else:
            return "Mix it up! Alternate between different task types."