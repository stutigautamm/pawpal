from dataclasses import dataclass, field
from typing import List, Dict, Any
import uuid

@dataclass
class Task:
    name: str
    duration: int  # in minutes
    priority: int  # e.g., 1 = Low, 2 = Medium, 3 = High
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    is_completed: bool = False

    def update_task(self, name: str, duration: int, priority: int) -> None:
        """Updates the task details."""
        pass

    def toggle_complete(self) -> None:
        """Toggles the task completion status."""
        pass


@dataclass
class Pet:
    name: str
    breed: str
    age: int
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Adds a care task to this specific pet's list."""
        pass

    def get_total_task_duration(self) -> int:
        """Calculates the sum of all task durations currently assigned to this pet."""
        pass


class Owner:
    def __init__(self, name: str, available_time_minutes: int):
        self.name: str = name
        self.available_time_minutes: int = available_time_minutes
        self.pets: List[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Links a new pet profile to the owner."""
        pass

    def update_availability(self, minutes: int) -> None:
        """Changes the total time available for scheduling today."""
        pass


class Scheduler:
    def __init__(self, owner: Owner):
        self.owner: Owner = owner
        self.daily_plan: List[Dict[str, Any]] = []
        self.reasoning_log: List[str] = []

    def generate_schedule(self) -> List[Dict[str, Any]]:
        """Gathers tasks, sorts them by priority/duration, and fits them into the owner's schedule."""
        pass

    def get_reasoning(self) -> str:
        """Returns a string explanation of why the schedule was built this way."""
        pass