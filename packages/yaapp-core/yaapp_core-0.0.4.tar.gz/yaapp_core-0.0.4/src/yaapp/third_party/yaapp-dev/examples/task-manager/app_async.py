#!/usr/bin/env python3
"""
Async Task Manager - Demonstrates YAPP async capabilities

This async version shows:
- Async database operations (simulated)
- Async task processing and notifications
- Async search and filtering
- Mixed sync/async operations
"""

import asyncio
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional
from enum import Enum
from dataclasses import dataclass, asdict
import json

# Add parent directory to path to import yaapp
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from yaapp import Yaapp

# Create yapp application
app = Yaapp()


class Priority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Status(Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    CANCELLED = "cancelled"


@dataclass
class Task:
    id: int
    title: str
    description: str
    priority: Priority
    status: Status
    created_at: datetime
    updated_at: datetime
    due_date: Optional[datetime] = None
    tags: List[str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []


class AsyncTaskStorage:
    """Simulate async database operations."""
    
    def __init__(self):
        self._tasks: Dict[int, Task] = {}
        self._next_id = 1
    
    async def save_task(self, task: Task) -> None:
        """Save task asynchronously."""
        # Simulate database write delay
        await asyncio.sleep(0.01)
        self._tasks[task.id] = task
    
    async def get_task(self, task_id: int) -> Optional[Task]:
        """Get task by ID asynchronously."""
        # Simulate database read delay
        await asyncio.sleep(0.005)
        return self._tasks.get(task_id)
    
    async def get_all_tasks(self) -> List[Task]:
        """Get all tasks asynchronously."""
        # Simulate database query delay
        await asyncio.sleep(0.02)
        return list(self._tasks.values())
    
    async def delete_task(self, task_id: int) -> bool:
        """Delete task asynchronously."""
        await asyncio.sleep(0.01)
        if task_id in self._tasks:
            del self._tasks[task_id]
            return True
        return False
    
    def get_next_id(self) -> int:
        """Get next available ID."""
        next_id = self._next_id
        self._next_id += 1
        return next_id


# Global storage instance
storage = AsyncTaskStorage()


# Async task management functions
@app.expose
async def create_task_async(
    title: str, 
    description: str = "", 
    priority: str = "medium",
    due_date: str = None,
    tags: str = ""
) -> Dict[str, Any]:
    """Create a new task asynchronously."""
    try:
        # Parse priority
        try:
            task_priority = Priority(priority.lower())
        except ValueError:
            return {"error": f"Invalid priority: {priority}"}
        
        # Parse due date
        task_due_date = None
        if due_date:
            try:
                task_due_date = datetime.fromisoformat(due_date)
            except ValueError:
                return {"error": f"Invalid due date format: {due_date}"}
        
        # Parse tags
        task_tags = [tag.strip() for tag in tags.split(",") if tag.strip()] if tags else []
        
        # Create task
        now = datetime.now()
        task = Task(
            id=storage.get_next_id(),
            title=title,
            description=description,
            priority=task_priority,
            status=Status.TODO,
            created_at=now,
            updated_at=now,
            due_date=task_due_date,
            tags=task_tags
        )
        
        # Save asynchronously
        await storage.save_task(task)
        
        return {
            "id": task.id,
            "title": task.title,
            "status": task.status.value,
            "priority": task.priority.value,
            "created_async": True
        }
    except Exception as e:
        return {"error": str(e)}


@app.expose
async def get_task_async(task_id: int) -> Dict[str, Any]:
    """Get task by ID asynchronously."""
    try:
        task = await storage.get_task(task_id)
        if not task:
            return {"error": f"Task {task_id} not found"}
        
        # Convert to dict with async processing
        await asyncio.sleep(0.005)  # Simulate processing
        
        task_dict = asdict(task)
        task_dict["priority"] = task.priority.value
        task_dict["status"] = task.status.value
        task_dict["created_at"] = task.created_at.isoformat()
        task_dict["updated_at"] = task.updated_at.isoformat()
        if task.due_date:
            task_dict["due_date"] = task.due_date.isoformat()
        
        task_dict["fetched_async"] = True
        return task_dict
    except Exception as e:
        return {"error": str(e)}


@app.expose
async def update_task_async(
    task_id: int,
    title: str = None,
    description: str = None,
    priority: str = None,
    status: str = None
) -> Dict[str, Any]:
    """Update task asynchronously."""
    try:
        task = await storage.get_task(task_id)
        if not task:
            return {"error": f"Task {task_id} not found"}
        
        # Update fields
        if title is not None:
            task.title = title
        if description is not None:
            task.description = description
        if priority is not None:
            try:
                task.priority = Priority(priority.lower())
            except ValueError:
                return {"error": f"Invalid priority: {priority}"}
        if status is not None:
            try:
                task.status = Status(status.lower())
            except ValueError:
                return {"error": f"Invalid status: {status}"}
        
        task.updated_at = datetime.now()
        
        # Save asynchronously
        await storage.save_task(task)
        
        return {
            "id": task.id,
            "title": task.title,
            "status": task.status.value,
            "updated_async": True
        }
    except Exception as e:
        return {"error": str(e)}


@app.expose
async def list_tasks_async(status: str = None, priority: str = None) -> Dict[str, Any]:
    """List tasks with optional filtering (async)."""
    try:
        tasks = await storage.get_all_tasks()
        
        # Filter by status
        if status:
            try:
                status_filter = Status(status.lower())
                tasks = [t for t in tasks if t.status == status_filter]
            except ValueError:
                return {"error": f"Invalid status: {status}"}
        
        # Filter by priority
        if priority:
            try:
                priority_filter = Priority(priority.lower())
                tasks = [t for t in tasks if t.priority == priority_filter]
            except ValueError:
                return {"error": f"Invalid priority: {priority}"}
        
        # Simulate processing delay for large lists
        if len(tasks) > 10:
            await asyncio.sleep(0.05)
        
        # Convert to dict format
        task_list = []
        for task in tasks:
            task_dict = {
                "id": task.id,
                "title": task.title,
                "status": task.status.value,
                "priority": task.priority.value,
                "created_at": task.created_at.isoformat(),
                "tags": task.tags
            }
            task_list.append(task_dict)
        
        return {
            "tasks": task_list,
            "count": len(task_list),
            "filtered_by": {
                "status": status,
                "priority": priority
            },
            "retrieved_async": True
        }
    except Exception as e:
        return {"error": str(e)}


# Async search functionality
@app.expose
async def search_tasks_async(query: str, search_tags: bool = True) -> Dict[str, Any]:
    """Search tasks asynchronously."""
    try:
        tasks = await storage.get_all_tasks()
        
        # Simulate complex search processing
        await asyncio.sleep(0.03)
        
        query_lower = query.lower()
        matching_tasks = []
        
        for task in tasks:
            matches = False
            
            # Search in title and description
            if (query_lower in task.title.lower() or 
                query_lower in task.description.lower()):
                matches = True
            
            # Search in tags if enabled
            if search_tags and any(query_lower in tag.lower() for tag in task.tags):
                matches = True
            
            if matches:
                matching_tasks.append({
                    "id": task.id,
                    "title": task.title,
                    "description": task.description[:100] + "..." if len(task.description) > 100 else task.description,
                    "priority": task.priority.value,
                    "status": task.status.value,
                    "tags": task.tags
                })
        
        return {
            "query": query,
            "matches": matching_tasks,
            "count": len(matching_tasks),
            "search_async": True
        }
    except Exception as e:
        return {"error": str(e)}


# Mixed sync/async class
@app.expose
class AsyncTaskAnalyzer:
    """Task analyzer with both sync and async methods."""
    
    async def get_overdue_tasks(self) -> Dict[str, Any]:
        """Get overdue tasks asynchronously."""
        try:
            tasks = await storage.get_all_tasks()
            now = datetime.now()
            
            # Simulate analysis processing
            await asyncio.sleep(0.02)
            
            overdue = []
            for task in tasks:
                if (task.due_date and 
                    task.due_date < now and 
                    task.status != Status.DONE):
                    
                    days_overdue = (now - task.due_date).days
                    overdue.append({
                        "id": task.id,
                        "title": task.title,
                        "due_date": task.due_date.isoformat(),
                        "days_overdue": days_overdue,
                        "priority": task.priority.value
                    })
            
            return {
                "overdue_tasks": overdue,
                "count": len(overdue),
                "analyzed_async": True
            }
        except Exception as e:
            return {"error": str(e)}
    
    def get_stats(self) -> Dict[str, Any]:
        """Get task statistics synchronously."""
        # This is sync for comparison
        try:
            # Note: This would need to be converted to async in real usage
            # For demo purposes, we'll return cached/estimated stats
            return {
                "total_tasks": "sync_estimated",
                "by_status": {
                    "todo": "sync_count",
                    "in_progress": "sync_count", 
                    "done": "sync_count"
                },
                "by_priority": {
                    "low": "sync_count",
                    "medium": "sync_count",
                    "high": "sync_count",
                    "urgent": "sync_count"
                },
                "computed_sync": True
            }
        except Exception as e:
            return {"error": str(e)}


# Async notification system
@app.expose
async def send_notifications_async(task_ids: List[int]) -> Dict[str, Any]:
    """Send notifications for tasks asynchronously."""
    try:
        notifications_sent = []
        
        for task_id in task_ids:
            task = await storage.get_task(task_id)
            if task:
                # Simulate sending notification
                await asyncio.sleep(0.01)
                
                notifications_sent.append({
                    "task_id": task.id,
                    "title": task.title,
                    "notification_type": "async_notification",
                    "sent_at": datetime.now().isoformat()
                })
        
        return {
            "notifications_sent": notifications_sent,
            "count": len(notifications_sent),
            "processing_async": True
        }
    except Exception as e:
        return {"error": str(e)}


# Bulk operations
@app.expose
async def bulk_update_status_async(task_ids: List[int], new_status: str) -> Dict[str, Any]:
    """Update multiple tasks' status asynchronously."""
    try:
        # Validate status
        try:
            status_value = Status(new_status.lower())
        except ValueError:
            return {"error": f"Invalid status: {new_status}"}
        
        updated_tasks = []
        failed_updates = []
        
        # Process tasks concurrently
        async def update_single_task(task_id):
            try:
                task = await storage.get_task(task_id)
                if task:
                    task.status = status_value
                    task.updated_at = datetime.now()
                    await storage.save_task(task)
                    return {"id": task_id, "success": True}
                else:
                    return {"id": task_id, "success": False, "error": "not_found"}
            except Exception as e:
                return {"id": task_id, "success": False, "error": str(e)}
        
        # Execute updates concurrently
        results = await asyncio.gather(
            *[update_single_task(task_id) for task_id in task_ids],
            return_exceptions=True
        )
        
        for result in results:
            if isinstance(result, dict):
                if result["success"]:
                    updated_tasks.append(result["id"])
                else:
                    failed_updates.append(result)
        
        return {
            "updated_tasks": updated_tasks,
            "failed_updates": failed_updates,
            "total_processed": len(task_ids),
            "success_count": len(updated_tasks),
            "bulk_async": True
        }
    except Exception as e:
        return {"error": str(e)}


# Custom async processor
class AsyncTaskProcessor:
    """Custom task processor with async capabilities."""
    
    def expose_to_registry(self, name: str, exposer) -> None:
        """Expose this processor to the registry."""
        pass
    
    async def execute_call(self, function_name: str, **kwargs) -> Any:
        """Execute processing functions asynchronously."""
        if function_name == "process_batch":
            return await self._process_batch(kwargs.get("batch_size", 10))
        elif function_name == "cleanup_old_tasks":
            return await self._cleanup_old_tasks(kwargs.get("days_old", 30))
        else:
            return {"error": f"Unknown function: {function_name}"}
    
    async def _process_batch(self, batch_size: int) -> Dict[str, Any]:
        """Process tasks in batches."""
        try:
            tasks = await storage.get_all_tasks()
            
            # Simulate batch processing
            batches_processed = 0
            for i in range(0, len(tasks), batch_size):
                batch = tasks[i:i + batch_size]
                # Simulate processing each batch
                await asyncio.sleep(0.02)
                batches_processed += 1
            
            return {
                "total_tasks": len(tasks),
                "batch_size": batch_size,
                "batches_processed": batches_processed,
                "processing_method": "async_batch"
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def _cleanup_old_tasks(self, days_old: int) -> Dict[str, Any]:
        """Clean up old completed tasks."""
        try:
            tasks = await storage.get_all_tasks()
            cutoff_date = datetime.now() - timedelta(days=days_old)
            
            # Simulate cleanup processing
            await asyncio.sleep(0.05)
            
            old_tasks = [
                task for task in tasks 
                if (task.status == Status.DONE and 
                    task.updated_at < cutoff_date)
            ]
            
            # Simulate cleanup (in real app, would delete)
            cleaned_count = len(old_tasks)
            
            return {
                "days_threshold": days_old,
                "tasks_found": cleaned_count,
                "cleanup_method": "async_processing",
                "cutoff_date": cutoff_date.isoformat()
            }
        except Exception as e:
            return {"error": str(e)}


# Expose the custom processor
async_processor = AsyncTaskProcessor()
app.expose(async_processor, name="async_processor", custom=True)


if __name__ == "__main__":
    print("🚀 Async Task Manager loaded!")
    print("This version demonstrates async task operations and notifications.")
    print("All functions support both sync and async execution contexts.")
    app.run()