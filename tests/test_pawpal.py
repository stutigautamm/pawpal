"""Simple tests for the PawPal system."""

import os
import sys

# Allow importing pawpal_system.py from the project root.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pawpal_system import Pet, Task, Priority


def test_task_completion():
    """Calling mark_complete() should flip the task's status."""
    task = Task("Give Medication", duration=5, priority=Priority.HIGH, pet_name="Rex")

    assert task.is_completed is False  # starts incomplete

    task.mark_complete()

    assert task.is_completed is True   # now marked complete


def test_task_addition():
    """Adding a task to a Pet should increase that pet's task count."""
    pet = Pet("Rex", "Golden Retriever", 3)

    assert len(pet.tasks) == 0

    pet.add_task(Task("Morning Walk", duration=30, priority=Priority.MEDIUM, pet_name="Rex"))

    assert len(pet.tasks) == 1
