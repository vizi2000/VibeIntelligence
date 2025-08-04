"""
Base Agent Class
Foundation for all background agents
Following Directive 8: Multi-agent system architecture
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime
import asyncio
import logging
from sqlalchemy.orm import Session

from ..models.agent_task import AgentTask, TaskStatus, TaskPriority, AgentType
from ..models.developer_activity import DeveloperActivity
from ..models.developer_profile import DeveloperProfile
from ..core.database import get_db
from ..ai.orchestrator import orchestrator, TaskType

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """
    Abstract base class for all agents
    Provides common functionality for task management and AI integration
    """
    
    def __init__(self, agent_type: AgentType, name: str):
        self.agent_type = agent_type
        self.name = name
        self.is_running = False
        self._tasks_queue: List[AgentTask] = []
        self._current_task: Optional[AgentTask] = None
        
    @abstractmethod
    async def execute_task(self, task: AgentTask, db: Session) -> Dict[str, Any]:
        """
        Execute a specific task
        Must be implemented by each agent
        """
        pass
    
    @abstractmethod
    async def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform agent-specific analysis
        Must be implemented by each agent
        """
        pass
    
    async def run(self) -> None:
        """Main agent loop"""
        self.is_running = True
        logger.info(f"🚀 {self.name} agent started")
        
        while self.is_running:
            try:
                # Get next task from queue
                task = await self._get_next_task()
                if not task:
                    await asyncio.sleep(10)  # Wait before checking again
                    continue
                
                # Execute task
                await self._execute_with_tracking(task)
                
            except Exception as e:
                logger.error(f"❌ {self.name} agent error: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def stop(self) -> None:
        """Stop the agent gracefully"""
        logger.info(f"🛑 Stopping {self.name} agent...")
        self.is_running = False
    
    async def _get_next_task(self) -> Optional[AgentTask]:
        """Get next task from database"""
        async for db in get_db():
            try:
                # Get pending tasks for this agent type
                task = db.query(AgentTask).filter(
                    AgentTask.agent_type == self.agent_type.value,
                    AgentTask.status == TaskStatus.PENDING
                ).order_by(
                    AgentTask.priority.desc(),
                    AgentTask.created_at
                ).first()
                
                if task:
                    # Mark as running
                    task.status = TaskStatus.RUNNING
                    task.started_at = datetime.utcnow()
                    db.commit()
                    return task
                    
            except Exception as e:
                logger.error(f"Error getting task: {e}")
                db.rollback()
            finally:
                await db.close()
        
        return None
    
    async def _execute_with_tracking(self, task: AgentTask) -> None:
        """Execute task with activity tracking"""
        start_time = datetime.utcnow()
        
        async for db in get_db():
            try:
                # Update task status
                self._current_task = task
                
                # Log activity start
                activity = DeveloperActivity(
                    developer_id=task.developer_id,
                    activity_type="agent_task",
                    action=f"{self.name} started: {task.task_name}",
                    session_id=f"agent_{self.agent_type.value}_{task.id}",
                    started_at=start_time,
                    details={
                        "agent_type": self.agent_type.value,
                        "task_id": task.id,
                        "task_name": task.task_name
                    }
                )
                db.add(activity)
                db.commit()
                
                # Execute the task
                result = await self.execute_task(task, db)
                
                # Update task with results
                task.status = TaskStatus.COMPLETED
                task.completed_at = datetime.utcnow()
                task.output_data = result
                task.execution_time_seconds = (task.completed_at - start_time).total_seconds()
                
                # Update activity
                activity.completed_at = task.completed_at
                activity.success = True
                activity.calculate_duration()
                
                # Schedule next run if recurring
                if task.is_recurring:
                    task.schedule_next_run()
                
                db.commit()
                logger.info(f"✅ {self.name} completed task: {task.task_name}")
                
            except Exception as e:
                logger.error(f"❌ Task execution failed: {e}")
                
                # Update task status
                task.status = TaskStatus.FAILED
                task.error_message = str(e)
                task.completed_at = datetime.utcnow()
                
                # Retry if possible
                if task.can_retry():
                    task.retry_count += 1
                    task.status = TaskStatus.PENDING
                    task.scheduled_at = datetime.utcnow()
                
                db.commit()
                
            finally:
                self._current_task = None
                await db.close()
    
    async def create_task(
        self,
        developer_id: int,
        task_name: str,
        description: str,
        input_data: Dict[str, Any],
        priority: TaskPriority = TaskPriority.MEDIUM,
        is_recurring: bool = False,
        recurrence_pattern: Optional[Dict[str, Any]] = None
    ) -> AgentTask:
        """Create a new task for this agent"""
        async for db in get_db():
            try:
                task = AgentTask(
                    developer_id=developer_id,
                    agent_type=self.agent_type.value,
                    task_name=task_name,
                    description=description,
                    priority=priority.value,
                    input_data=input_data,
                    is_recurring=is_recurring,
                    recurrence_pattern=recurrence_pattern
                )
                
                db.add(task)
                db.commit()
                db.refresh(task)
                
                logger.info(f"📋 Created task: {task_name} for {self.name}")
                return task
                
            finally:
                await db.close()
    
    async def log_activity(
        self,
        developer_id: int,
        action: str,
        target: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log agent activity"""
        async for db in get_db():
            try:
                activity = DeveloperActivity(
                    developer_id=developer_id,
                    activity_type=f"agent_{self.agent_type.value}",
                    action=action,
                    target=target,
                    details=details or {},
                    started_at=datetime.utcnow(),
                    completed_at=datetime.utcnow()
                )
                activity.calculate_duration()
                
                db.add(activity)
                db.commit()
                
            except Exception as e:
                logger.error(f"Failed to log activity: {e}")
            finally:
                await db.close()
    
    async def use_ai(
        self,
        prompt: str,
        task_type: TaskType = TaskType.GENERAL_CHAT,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Use AI orchestrator for agent tasks"""
        try:
            response = await orchestrator.generate(
                prompt=prompt,
                task_type=task_type,
                context=context,
                temperature=0.7
            )
            
            # Track AI usage in current task
            if self._current_task:
                self._current_task.ai_provider = response.get("provider")
                self._current_task.ai_model = response.get("model")
                self._current_task.tokens_used = response.get("tokens", 0)
                self._current_task.cost = response.get("cost", 0.0)
            
            return response
            
        except Exception as e:
            logger.error(f"AI request failed: {e}")
            raise
    
    def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            "agent_type": self.agent_type.value,
            "name": self.name,
            "is_running": self.is_running,
            "current_task": self._current_task.task_name if self._current_task else None,
            "queue_size": len(self._tasks_queue)
        }