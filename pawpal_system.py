from dataclasses import dataclass, field
from datetime import date, timedelta
from enum import Enum, IntEnum
from typing import List, Optional
import uuid


class Priority(IntEnum):
    """Task priority. Higher value = more urgent, so it sorts naturally."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3


class Frequency(str, Enum):
    """How often a task recurs. ONCE tasks never regenerate; DAILY/WEEKLY do."""
    ONCE = "once"
    DAILY = "daily"
    WEEKLY = "weekly"


# How many days to advance the due date when a recurring task is completed.
_RECUR_DAYS = {Frequency.DAILY: 1, Frequency.WEEKLY: 7}


def _validate_time(value: str) -> str:
    """Ensure a time string is zero-padded 'HH:MM' (e.g. '09:05'). Returns it unchanged."""
    try:
        hours, minutes = value.split(":")
    except (AttributeError, ValueError):
        raise ValueError(f"time must be in 'HH:MM' format, got {value!r}")
    if (
        len(hours) != 2
        or len(minutes) != 2
        or not (0 <= int(hours) <= 23)
        or not (0 <= int(minutes) <= 59)
    ):
        raise ValueError(f"time must be a valid zero-padded 'HH:MM', got {value!r}")
    return value


@dataclass
class Task:
    """A single care activity assigned to a pet."""
    name: str
    duration: int  # minutes
    priority: Priority
    pet_name: str  # links the task back to its pet for clear scheduling output
    time: str = "00:00"  # scheduled start, zero-padded 'HH:MM' (24-hour)
    frequency: Frequency = Frequency.ONCE
    due_date: date = field(default_factory=date.today)  # calendar day the task is due
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    is_completed: bool = False

    def __post_init__(self) -> None:
        """Validate the time string once the dataclass is built."""
        self.time = _validate_time(self.time)
        self.frequency = Frequency(self.frequency)

    def next_occurrence(self) -> Optional["Task"]:
        """Build the follow-up task for the next cycle of a recurring task.

        The copy keeps name, duration, priority, pet, time, and frequency, but
        gets a brand-new id and starts incomplete. Its ``due_date`` is advanced
        with ``timedelta`` off the *current* due date — +1 day for DAILY, +7 for
        WEEKLY — so repeated completions walk the date forward correctly.

        Returns:
            A new incomplete Task dated for the next occurrence, or ``None`` if
            this task is one-off (``Frequency.ONCE``) and therefore never recurs.
        """
        if self.frequency == Frequency.ONCE:
            return None
        next_due = self.due_date + timedelta(days=_RECUR_DAYS[self.frequency])
        return Task(
            name=self.name,
            duration=self.duration,
            priority=self.priority,
            pet_name=self.pet_name,
            time=self.time,
            frequency=self.frequency,
            due_date=next_due,
        )

    def update_task(
        self,
        name: Optional[str] = None,
        duration: Optional[int] = None,
        priority: Optional[Priority] = None,
        time: Optional[str] = None,
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
        if time is not None:
            self.time = _validate_time(time)

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

    def complete_task(self, task_id: str) -> Optional[Task]:
        """Mark a task complete and, if it recurs, spawn its next occurrence.

        Guards on the already-complete case so a double-click can't spawn
        duplicate follow-ups.

        Args:
            task_id: id of the task on this pet to complete.

        Returns:
            The newly-created follow-up Task for a DAILY/WEEKLY task, or ``None``
            if the task was one-off, wasn't found on this pet, or was already
            complete.
        """
        task = next((t for t in self.tasks if t.id == task_id), None)
        if task is None or task.is_completed:
            return None
        task.is_completed = True
        follow_up = task.next_occurrence()
        if follow_up is not None:
            self.add_task(follow_up)  # new id, so the idempotency guard lets it in
        return follow_up

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
    
    def filter_tasks(
        self,
        is_completed: Optional[bool] = None,
        pet_name: Optional[str] = None,
    ) -> List[Task]:
        """Return tasks matching the given filters.

        The two filters are independent and combine with AND.

        Args:
            is_completed: if given, keep only tasks whose completion status
                equals this (``True`` = done, ``False`` = pending).
            pet_name: if given, keep only tasks belonging to this pet.

        Returns:
            A new list of matching tasks (every task when no filters are passed).
        """
        tasks = self.get_all_tasks()
        if is_completed is not None:
            tasks = [t for t in tasks if t.is_completed == is_completed]
        if pet_name is not None:
            tasks = [t for t in tasks if t.pet_name == pet_name]
        return tasks


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
    
    def sort_by_time(self) -> List[Task]:
        """Return the current daily plan sorted chronologically by start time.

        Because each task's ``time`` is a zero-padded 'HH:MM' string, a plain
        lambda key works: string comparison already orders '09:30' before
        '14:05'. 

        Returns:
            A new list of the ``daily_plan`` tasks ordered by ``time``; the
            stored plan itself is left untouched.
        """
        return sorted(self.daily_plan, key=lambda t: t.time)

    def detect_conflicts(self) -> List[str]:
        """Find pending tasks that share the same start time (a lightweight check).

        Groups incomplete tasks by their ``time`` and flags any slot holding more
        than one task — whether they belong to the same pet or different pets.
        Returns a list of human-readable warning strings (empty if no conflicts);
        it never raises, so callers can print warnings and keep going.
        """
        by_time: dict = {}
        for task in self.owner.filter_tasks(is_completed=False):
            by_time.setdefault(task.time, []).append(task)

        warnings: List[str] = []
        for time in sorted(by_time):
            clashing = by_time[time]
            if len(clashing) < 2:
                continue
            labels = ", ".join(f"'{t.name}' ({t.pet_name})" for t in clashing)
            pets = {t.pet_name for t in clashing}
            scope = "same pet" if len(pets) == 1 else f"{len(pets)} pets"
            warnings.append(
                f"WARNING - Conflict at {time}: {len(clashing)} tasks ({scope}) - {labels}."
            )
        return warnings

    def mark_task_complete(self, task_id: str) -> Optional[Task]:
        """Complete a task by id across any of the owner's pets.

        Finds the pet that owns the task and delegates to ``Pet.complete_task``,
        so recurring tasks automatically regenerate. Returns the follow-up Task
        if one was spawned, else ``None``.
        """
        for pet in self.owner.pets:
            if any(t.id == task_id for t in pet.tasks):
                return pet.complete_task(task_id)
        return None

    def get_reasoning(self) -> str:
        """Human-readable explanation of the most recent schedule."""
        if not self.reasoning_log:
            return "No schedule has been generated yet."
        return "\n".join(self.reasoning_log)
