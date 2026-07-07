from dataclasses import dataclass, field
from enum import IntEnum
from typing import List, Optional
import uuid


class Priority(IntEnum):
    """Task priority. Higher value = more urgent, so it sorts naturally."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3


@dataclass
class Task:
    """A single care activity assigned to a pet."""
    name: str
    duration: int  # minutes
    priority: Priority
    pet_name: str  # links the task back to its pet for clear scheduling output
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    is_completed: bool = False

    def update_task(
        self,
        name: Optional[str] = None,
        duration: Optional[int] = None,
        priority: Optional[Priority] = None,
    ) -> None:
        """Update editable task details. Only the arguments passed are changed."""
        if name is not None:
            self.name = name
        if duration is not None:
            if duration < 0:
                raise ValueError("duration cannot be negative")
            self.duration = duration
        if priority is not None:
            self.priority = Priority(priority)

    def mark_complete(self) -> None:
        """Flip the completion status."""
        self.is_completed = not self.is_completed


@dataclass
class Pet:
    """A pet profile and the care tasks assigned to it."""
    name: str
    breed: str
    age: int
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Assign a task to this pet, stamping the back-reference. Idempotent by task id."""
        if any(t.id == task.id for t in self.tasks):
            return
        task.pet_name = self.name
        self.tasks.append(task)

    def remove_task(self, task_id: str) -> bool:
        """Remove a task by id. Returns True if a task was removed."""
        before = len(self.tasks)
        self.tasks = [t for t in self.tasks if t.id != task_id]
        return len(self.tasks) < before

    def get_total_task_duration(self) -> int:
        """Total minutes across every task assigned to this pet (completed or not)."""
        return sum(t.duration for t in self.tasks)


class Owner:
    """The app user. Owns pets and sets the day's time budget."""

    def __init__(self, name: str, available_time_minutes: int):
        """Create an owner with a name and today's time budget in minutes."""
        if available_time_minutes < 0:
            raise ValueError("available_time_minutes cannot be negative")
        self.name: str = name
        self.available_time_minutes: int = available_time_minutes
        self.pets: List[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Link a pet profile to this owner. Idempotent — adding the same pet twice is a no-op."""
        if pet not in self.pets:
            self.pets.append(pet)

    def update_availability(self, minutes: int) -> None:
        """Change today's total available time."""
        if minutes < 0:
            raise ValueError("minutes cannot be negative")
        self.available_time_minutes = minutes

    def get_all_tasks(self) -> List[Task]:
        """Flatten every task across all of the owner's pets into one list."""
        return [task for pet in self.pets for task in pet.tasks]


class Scheduler:
    """The 'brain': turns the owner's pets/tasks into a time-bounded daily plan."""

    def __init__(self, owner: Owner):
        """Create a scheduler bound to one owner, with empty plan and log."""
        self.owner: Owner = owner
        self.daily_plan: List[Task] = []
        self.reasoning_log: List[str] = []

    def generate_schedule(self) -> List[Task]:
        """Build the daily plan.

        Strategy: gather all incomplete tasks, sort by priority (highest first)
        then duration (shortest first), and greedily fit them into the owner's
        available time. If a task doesn't fit, it is *skipped* (not a hard stop),
        so a large high-priority task can't starve smaller tasks behind it. Every
        decision is recorded in ``reasoning_log``.
        """
        self.daily_plan = []
        self.reasoning_log = []

        budget = self.owner.available_time_minutes
        remaining = budget

        all_tasks = self.owner.get_all_tasks()
        pending = [t for t in all_tasks if not t.is_completed]
        skipped_completed = len(all_tasks) - len(pending)

        self.reasoning_log.append(
            f"Starting schedule for {self.owner.name} with {budget} min available."
        )
        if skipped_completed:
            self.reasoning_log.append(
                f"Ignored {skipped_completed} already-completed task(s)."
            )
        if not pending:
            self.reasoning_log.append("No pending tasks to schedule.")
            return self.daily_plan

        # Highest priority first; among equal priority, shortest first so more fit.
        ordered = sorted(pending, key=lambda t: (-int(t.priority), t.duration))

        for task in ordered:
            label = f"'{task.name}' for {task.pet_name} ({task.priority.name}, {task.duration} min)"
            if task.duration <= remaining:
                self.daily_plan.append(task)
                remaining -= task.duration
                self.reasoning_log.append(
                    f"Scheduled {label}. {remaining} min left."
                )
            else:
                self.reasoning_log.append(
                    f"Skipped {label} — needs {task.duration} min but only {remaining} left."
                )

        self.reasoning_log.append(
            f"Final plan: {len(self.daily_plan)} of {len(pending)} pending task(s), "
            f"{budget - remaining} of {budget} min used."
        )
        return self.daily_plan

    def get_reasoning(self) -> str:
        """Human-readable explanation of the most recent schedule."""
        if not self.reasoning_log:
            return "No schedule has been generated yet."
        return "\n".join(self.reasoning_log)
