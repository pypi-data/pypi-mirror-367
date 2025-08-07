#!/usr/bin/env python3
"""
Task Manager - A practical example using YAPP

This example demonstrates:
- Stateful operations with persistent data
- CRUD operations (Create, Read, Update, Delete)
- Complex business logic
- Data validation and error handling
- JSON file persistence
"""

import json
import sys
from dataclasses import asdict, dataclass
from datetime import date, datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

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
    priority: str
    status: str
    created_at: str
    due_date: Optional[str] = None
    completed_at: Optional[str] = None
    tags: List[str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []


class TaskManager:
    """Core task management functionality."""

    def __init__(self, data_file: str = "tasks.json"):
        self.data_file = Path(data_file)
        self.tasks: Dict[int, Task] = {}
        self.next_id = 1
        self.load_tasks()

    def load_tasks(self):
        """Load tasks from JSON file."""
        if self.data_file.exists():
            try:
                with open(self.data_file, "r") as f:
                    data = json.load(f)
                    self.next_id = data.get("next_id", 1)
                    for task_data in data.get("tasks", []):
                        task = Task(**task_data)
                        self.tasks[task.id] = task
            except Exception as e:
                print(f"Error loading tasks: {e}")

    def save_tasks(self):
        """Save tasks to JSON file."""
        try:
            data = {
                "next_id": self.next_id,
                "tasks": [asdict(task) for task in self.tasks.values()],
            }
            with open(self.data_file, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving tasks: {e}")

    def create_task(
        self,
        title: str,
        description: str = "",
        priority: str = "medium",
        due_date: Optional[str] = None,
        tags: List[str] = None,
    ) -> Dict[str, Any]:
        """Create a new task."""
        try:
            # Validate priority
            if priority not in [p.value for p in Priority]:
                return {
                    "error": f"Invalid priority. Must be one of: {[p.value for p in Priority]}"
                }

            # Validate due_date format if provided
            if due_date:
                try:
                    datetime.strptime(due_date, "%Y-%m-%d")
                except ValueError:
                    return {"error": "Invalid due_date format. Use YYYY-MM-DD"}

            task = Task(
                id=self.next_id,
                title=title,
                description=description,
                priority=priority,
                status=Status.TODO.value,
                created_at=datetime.now().isoformat(),
                due_date=due_date,
                tags=tags or [],
            )

            self.tasks[task.id] = task
            self.next_id += 1
            self.save_tasks()

            return {"success": True, "task": asdict(task)}
        except Exception as e:
            return {"error": str(e)}

    def get_task(self, task_id: int) -> Dict[str, Any]:
        """Get a specific task by ID."""
        if task_id not in self.tasks:
            return {"error": f"Task {task_id} not found"}
        return {"task": asdict(self.tasks[task_id])}

    def update_task(self, task_id: int, **kwargs) -> Dict[str, Any]:
        """Update an existing task."""
        if task_id not in self.tasks:
            return {"error": f"Task {task_id} not found"}

        task = self.tasks[task_id]

        # Validate updates
        if "priority" in kwargs and kwargs["priority"] not in [
            p.value for p in Priority
        ]:
            return {
                "error": f"Invalid priority. Must be one of: {[p.value for p in Priority]}"
            }

        if "status" in kwargs and kwargs["status"] not in [s.value for s in Status]:
            return {
                "error": f"Invalid status. Must be one of: {[s.value for s in Status]}"
            }

        if "due_date" in kwargs and kwargs["due_date"]:
            try:
                datetime.strptime(kwargs["due_date"], "%Y-%m-%d")
            except ValueError:
                return {"error": "Invalid due_date format. Use YYYY-MM-DD"}

        # Update task fields
        for key, value in kwargs.items():
            if hasattr(task, key):
                setattr(task, key, value)

        # Set completion timestamp if marking as done
        if kwargs.get("status") == Status.DONE.value and not task.completed_at:
            task.completed_at = datetime.now().isoformat()

        self.save_tasks()
        return {"success": True, "task": asdict(task)}

    def delete_task(self, task_id: int) -> Dict[str, Any]:
        """Delete a task."""
        if task_id not in self.tasks:
            return {"error": f"Task {task_id} not found"}

        deleted_task = self.tasks.pop(task_id)
        self.save_tasks()
        return {"success": True, "deleted_task": asdict(deleted_task)}

    def list_tasks(
        self,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        tag: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List tasks with optional filtering."""
        tasks = list(self.tasks.values())

        # Apply filters
        if status:
            tasks = [t for t in tasks if t.status == status]
        if priority:
            tasks = [t for t in tasks if t.priority == priority]
        if tag:
            tasks = [t for t in tasks if tag in t.tags]

        # Sort by created_at
        tasks.sort(key=lambda t: t.created_at, reverse=True)

        return {"total": len(tasks), "tasks": [asdict(task) for task in tasks]}

    def get_stats(self) -> Dict[str, Any]:
        """Get task statistics."""
        all_tasks = list(self.tasks.values())

        stats = {
            "total_tasks": len(all_tasks),
            "by_status": {},
            "by_priority": {},
            "overdue_tasks": 0,
            "completed_today": 0,
        }

        today = date.today().isoformat()

        for task in all_tasks:
            # Count by status
            stats["by_status"][task.status] = stats["by_status"].get(task.status, 0) + 1

            # Count by priority
            stats["by_priority"][task.priority] = (
                stats["by_priority"].get(task.priority, 0) + 1
            )

            # Count overdue tasks
            if task.due_date and task.status != Status.DONE.value:
                if task.due_date < today:
                    stats["overdue_tasks"] += 1

            # Count completed today
            if task.completed_at and task.completed_at.startswith(today):
                stats["completed_today"] += 1

        return stats


# Initialize task manager
task_manager = TaskManager()


# Expose task management functionality
@app.expose
def create_task(
    title: str,
    description: str = "",
    priority: str = "medium",
    due_date: Optional[str] = None,
    tags: Optional[str] = None,
) -> Dict[str, Any]:
    """Create a new task."""
    tag_list = tags.split(",") if tags else []
    tag_list = [tag.strip() for tag in tag_list if tag.strip()]
    return task_manager.create_task(title, description, priority, due_date, tag_list)


@app.expose
def get_task(task_id: int) -> Dict[str, Any]:
    """Get a specific task by ID."""
    return task_manager.get_task(task_id)


@app.expose
def update_task(
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    priority: Optional[str] = None,
    status: Optional[str] = None,
    due_date: Optional[str] = None,
    tags: Optional[str] = None,
) -> Dict[str, Any]:
    """Update an existing task."""
    updates = {}
    if title is not None:
        updates["title"] = title
    if description is not None:
        updates["description"] = description
    if priority is not None:
        updates["priority"] = priority
    if status is not None:
        updates["status"] = status
    if due_date is not None:
        updates["due_date"] = due_date
    if tags is not None:
        tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
        updates["tags"] = tag_list

    return task_manager.update_task(task_id, **updates)


@app.expose
def delete_task(task_id: int) -> Dict[str, Any]:
    """Delete a task."""
    return task_manager.delete_task(task_id)


@app.expose
def list_tasks(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    tag: Optional[str] = None,
) -> Dict[str, Any]:
    """List tasks with optional filtering."""
    return task_manager.list_tasks(status, priority, tag)


@app.expose
def get_stats() -> Dict[str, Any]:
    """Get task statistics."""
    return task_manager.get_stats()


# Expose utility functions via dictionary tree
app.expose(
    {
        "quick": {
            "add_urgent": lambda title: task_manager.create_task(
                title, priority="urgent"
            ),
            "mark_done": lambda task_id: task_manager.update_task(
                int(task_id), status="done"
            ),
            "mark_progress": lambda task_id: task_manager.update_task(
                int(task_id), status="in_progress"
            ),
        },
        "search": {
            "by_status": lambda status: task_manager.list_tasks(status=status),
            "by_priority": lambda priority: task_manager.list_tasks(priority=priority),
            "by_tag": lambda tag: task_manager.list_tasks(tag=tag),
            "overdue": lambda: [
                asdict(t)
                for t in task_manager.tasks.values()
                if t.due_date
                and t.due_date < date.today().isoformat()
                and t.status != "done"
            ],
        },
        "reports": {
            "daily_summary": lambda: {
                "stats": task_manager.get_stats(),
                "todo_today": [
                    asdict(t)
                    for t in task_manager.tasks.values()
                    if t.status == "todo"
                    and (not t.due_date or t.due_date <= date.today().isoformat())
                ],
            },
            "priority_summary": lambda: {
                priority.value: len(
                    [
                        t
                        for t in task_manager.tasks.values()
                        if t.priority == priority.value
                    ]
                )
                for priority in Priority
            },
        },
    }
)

if __name__ == "__main__":
    app.run()
