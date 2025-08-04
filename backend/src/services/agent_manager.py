"""
Agent Manager Service
Manages all background agents and task queues
Following Directive 8: Multi-agent orchestration
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from ..agents.base_agent import BaseAgent
from ..agents.documentation_agent import DocumentationAgent
from ..models.agent_task import AgentTask, TaskStatus, TaskPriority, AgentType, AgentSchedule
from ..models.developer_profile import DeveloperProfile
from ..core.database import get_db
from ..core.config import settings

logger = logging.getLogger(__name__)


class AgentManager:
    """
    Central manager for all agents
    Handles task scheduling, agent lifecycle, and monitoring
    """
    
    def __init__(self):
        self.agents: Dict[AgentType, BaseAgent] = {}
        self.is_running = False
        self._scheduler_task: Optional[asyncio.Task] = None
        self._monitor_task: Optional[asyncio.Task] = None
        self._agent_tasks: Dict[AgentType, asyncio.Task] = {}
    
    async def initialize(self) -> None:
        """Initialize all agents"""
        logger.info("🚀 Initializing Agent Manager...")
        
        # Initialize individual agents
        self.agents[AgentType.DOCUMENTATION] = DocumentationAgent()
        
        # More agents to be added:
        # self.agents[AgentType.SCANNER] = ScannerAgent()
        # self.agents[AgentType.ANALYZER] = AnalyzerAgent()
        # self.agents[AgentType.MONETIZATION] = MonetizationAgent()
        # self.agents[AgentType.SKILL_TRACKER] = SkillTrackerAgent()
        
        logger.info(f"✅ Initialized {len(self.agents)} agents")
    
    async def start(self) -> None:
        """Start all agents and schedulers"""
        if self.is_running:
            logger.warning("Agent Manager already running")
            return
        
        self.is_running = True
        logger.info("🎯 Starting Agent Manager...")
        
        # Start individual agents
        for agent_type, agent in self.agents.items():
            self._agent_tasks[agent_type] = asyncio.create_task(agent.run())
            logger.info(f"✅ Started {agent.name}")
        
        # Start scheduler
        self._scheduler_task = asyncio.create_task(self._run_scheduler())
        
        # Start monitor
        self._monitor_task = asyncio.create_task(self._run_monitor())
        
        logger.info("🎉 Agent Manager started successfully")
    
    async def stop(self) -> None:
        """Stop all agents gracefully"""
        logger.info("🛑 Stopping Agent Manager...")
        self.is_running = False
        
        # Stop all agents
        for agent in self.agents.values():
            await agent.stop()
        
        # Cancel tasks
        for task in self._agent_tasks.values():
            task.cancel()
        
        if self._scheduler_task:
            self._scheduler_task.cancel()
        
        if self._monitor_task:
            self._monitor_task.cancel()
        
        # Wait for cancellation
        await asyncio.gather(
            *self._agent_tasks.values(),
            self._scheduler_task,
            self._monitor_task,
            return_exceptions=True
        )
        
        logger.info("👋 Agent Manager stopped")
    
    async def create_task(
        self,
        developer_id: int,
        agent_type: AgentType,
        task_name: str,
        description: str,
        input_data: Dict[str, Any],
        priority: TaskPriority = TaskPriority.MEDIUM,
        scheduled_at: Optional[datetime] = None,
        is_recurring: bool = False,
        recurrence_pattern: Optional[Dict[str, Any]] = None
    ) -> AgentTask:
        """Create a new agent task"""
        agent = self.agents.get(agent_type)
        if not agent:
            raise ValueError(f"Agent type {agent_type} not available")
        
        task = await agent.create_task(
            developer_id=developer_id,
            task_name=task_name,
            description=description,
            input_data=input_data,
            priority=priority,
            is_recurring=is_recurring,
            recurrence_pattern=recurrence_pattern
        )
        
        if scheduled_at:
            task.scheduled_at = scheduled_at
            task.status = TaskStatus.SCHEDULED
        
        return task
    
    async def _run_scheduler(self) -> None:
        """Run task scheduler loop"""
        logger.info("📅 Task scheduler started")
        
        while self.is_running:
            try:
                await self._process_scheduled_tasks()
                await self._process_recurring_tasks()
                await self._cleanup_old_tasks()
                
                # Check every minute
                await asyncio.sleep(60)
                
            except Exception as e:
                logger.error(f"Scheduler error: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes on error
    
    async def _process_scheduled_tasks(self) -> None:
        """Process tasks scheduled for execution"""
        async for db in get_db():
            try:
                # Find scheduled tasks ready to run
                now = datetime.utcnow()
                scheduled_tasks = db.query(AgentTask).filter(
                    AgentTask.status == TaskStatus.SCHEDULED,
                    AgentTask.scheduled_at <= now
                ).all()
                
                for task in scheduled_tasks:
                    # Check agent schedule limits
                    if await self._can_run_task(task, db):
                        task.status = TaskStatus.PENDING
                        db.commit()
                        logger.info(f"📋 Activated scheduled task: {task.task_name}")
                
            except Exception as e:
                logger.error(f"Error processing scheduled tasks: {e}")
                db.rollback()
            finally:
                await db.close()
    
    async def _process_recurring_tasks(self) -> None:
        """Process recurring tasks"""
        async for db in get_db():
            try:
                # Find completed recurring tasks that need to be rescheduled
                recurring_tasks = db.query(AgentTask).filter(
                    AgentTask.is_recurring == True,
                    AgentTask.status == TaskStatus.COMPLETED,
                    AgentTask.next_run_at <= datetime.utcnow()
                ).all()
                
                for task in recurring_tasks:
                    # Create new instance of recurring task
                    new_task = AgentTask(
                        developer_id=task.developer_id,
                        agent_type=task.agent_type,
                        task_name=task.task_name,
                        description=task.description,
                        priority=task.priority,
                        input_data=task.input_data,
                        is_recurring=True,
                        recurrence_pattern=task.recurrence_pattern,
                        scheduled_at=task.next_run_at
                    )
                    
                    db.add(new_task)
                    
                    # Update original task
                    task.schedule_next_run()
                    
                db.commit()
                
            except Exception as e:
                logger.error(f"Error processing recurring tasks: {e}")
                db.rollback()
            finally:
                await db.close()
    
    async def _cleanup_old_tasks(self) -> None:
        """Clean up old completed tasks"""
        async for db in get_db():
            try:
                # Delete tasks older than 30 days
                cutoff_date = datetime.utcnow() - timedelta(days=30)
                old_tasks = db.query(AgentTask).filter(
                    AgentTask.status.in_([TaskStatus.COMPLETED, TaskStatus.FAILED]),
                    AgentTask.completed_at < cutoff_date,
                    AgentTask.is_recurring == False
                ).all()
                
                for task in old_tasks:
                    db.delete(task)
                
                if old_tasks:
                    db.commit()
                    logger.info(f"🧹 Cleaned up {len(old_tasks)} old tasks")
                
            except Exception as e:
                logger.error(f"Error cleaning up tasks: {e}")
                db.rollback()
            finally:
                await db.close()
    
    async def _can_run_task(self, task: AgentTask, db: Session) -> bool:
        """Check if task can run based on agent schedule limits"""
        # Get agent schedule
        schedule = db.query(AgentSchedule).filter(
            AgentSchedule.developer_id == task.developer_id,
            AgentSchedule.agent_type == task.agent_type
        ).first()
        
        if not schedule or not schedule.enabled:
            return True
        
        # Check daily limits
        if schedule.daily_runs_count >= schedule.max_daily_runs:
            return False
        
        if schedule.daily_tokens_used >= schedule.max_tokens_per_run:
            return False
        
        if schedule.daily_cost_used >= schedule.max_cost_per_day:
            return False
        
        # Check preferred hours
        current_hour = datetime.utcnow().hour
        if schedule.preferred_hours and current_hour not in schedule.preferred_hours:
            return False
        
        return True
    
    async def _run_monitor(self) -> None:
        """Monitor agent health and performance"""
        logger.info("📊 Agent monitor started")
        
        while self.is_running:
            try:
                stats = await self.get_system_stats()
                
                # Log system health
                logger.info(f"💓 System Stats: {stats['running_agents']}/{stats['total_agents']} agents running")
                logger.info(f"📋 Tasks: {stats['pending_tasks']} pending, {stats['running_tasks']} running")
                
                # Check for stuck tasks
                await self._check_stuck_tasks()
                
                # Reset daily limits if needed
                await self._reset_daily_limits()
                
                # Monitor every 5 minutes
                await asyncio.sleep(300)
                
            except Exception as e:
                logger.error(f"Monitor error: {e}")
                await asyncio.sleep(600)  # Wait 10 minutes on error
    
    async def _check_stuck_tasks(self) -> None:
        """Check for tasks stuck in running state"""
        async for db in get_db():
            try:
                # Find tasks running for too long
                timeout = datetime.utcnow() - timedelta(hours=1)
                stuck_tasks = db.query(AgentTask).filter(
                    AgentTask.status == TaskStatus.RUNNING,
                    AgentTask.started_at < timeout
                ).all()
                
                for task in stuck_tasks:
                    logger.warning(f"⚠️ Found stuck task: {task.task_name}")
                    task.status = TaskStatus.FAILED
                    task.error_message = "Task timeout - stuck in running state"
                    task.completed_at = datetime.utcnow()
                
                if stuck_tasks:
                    db.commit()
                
            except Exception as e:
                logger.error(f"Error checking stuck tasks: {e}")
                db.rollback()
            finally:
                await db.close()
    
    async def _reset_daily_limits(self) -> None:
        """Reset daily agent schedule limits"""
        async for db in get_db():
            try:
                # Find schedules that need reset
                yesterday = datetime.utcnow() - timedelta(days=1)
                schedules = db.query(AgentSchedule).filter(
                    AgentSchedule.last_reset_at < yesterday
                ).all()
                
                for schedule in schedules:
                    schedule.daily_runs_count = 0
                    schedule.daily_tokens_used = 0
                    schedule.daily_cost_used = 0.0
                    schedule.last_reset_at = datetime.utcnow()
                
                if schedules:
                    db.commit()
                    logger.info(f"🔄 Reset daily limits for {len(schedules)} schedules")
                
            except Exception as e:
                logger.error(f"Error resetting daily limits: {e}")
                db.rollback()
            finally:
                await db.close()
    
    async def get_system_stats(self) -> Dict[str, Any]:
        """Get system statistics"""
        stats = {
            "total_agents": len(self.agents),
            "running_agents": sum(1 for a in self.agents.values() if a.is_running),
            "pending_tasks": 0,
            "running_tasks": 0,
            "completed_today": 0,
            "failed_today": 0
        }
        
        async for db in get_db():
            try:
                # Count tasks by status
                today = datetime.utcnow().date()
                
                stats["pending_tasks"] = db.query(AgentTask).filter(
                    AgentTask.status == TaskStatus.PENDING
                ).count()
                
                stats["running_tasks"] = db.query(AgentTask).filter(
                    AgentTask.status == TaskStatus.RUNNING
                ).count()
                
                stats["completed_today"] = db.query(AgentTask).filter(
                    AgentTask.status == TaskStatus.COMPLETED,
                    AgentTask.completed_at >= today
                ).count()
                
                stats["failed_today"] = db.query(AgentTask).filter(
                    AgentTask.status == TaskStatus.FAILED,
                    AgentTask.completed_at >= today
                ).count()
                
            except Exception as e:
                logger.error(f"Error getting stats: {e}")
            finally:
                await db.close()
        
        return stats
    
    def get_agent_status(self, agent_type: AgentType) -> Optional[Dict[str, Any]]:
        """Get status of specific agent"""
        agent = self.agents.get(agent_type)
        if agent:
            return agent.get_status()
        return None
    
    def get_all_agents_status(self) -> List[Dict[str, Any]]:
        """Get status of all agents"""
        return [agent.get_status() for agent in self.agents.values()]


# Global agent manager instance
agent_manager = AgentManager()