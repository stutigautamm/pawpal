"""Simple tests for the PawPal system."""

import os
import sys
from datetime import date, timedelta

import pytest

# Allow importing pawpal_system.py from the project root.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pawpal_system import (
    Owner,
    Pet,
    Task,
    Priority,
    Frequency,
    Scheduler,
)


# --------------------------------------------------------------------------- #
# Existing basics
# --------------------------------------------------------------------------- #
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


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def _owner_with(*tasks, minutes=180):
    """Build an Owner/Pet/Scheduler wrapping the given tasks."""
    owner = Owner("Tester", available_time_minutes=minutes)
    pet = Pet("Rex", "Golden Retriever", 3)
    owner.add_pet(pet)
    for task in tasks:
        pet.add_task(task)
    return owner, pet, Scheduler(owner)


# --------------------------------------------------------------------------- #
# 1. Sorting correctness
# --------------------------------------------------------------------------- #
def test_sort_by_time_returns_chronological_order():
    """sort_by_time() returns the plan ordered by start time, regardless of add order."""
    # Added deliberately out of chronological order.
    evening = Task("Grooming", 30, Priority.LOW, "Rex", time="18:30")
    morning = Task("Walk", 30, Priority.MEDIUM, "Rex", time="07:15")
    midday = Task("Vet", 15, Priority.HIGH, "Rex", time="12:00")
    owner, pet, scheduler = _owner_with(evening, morning, midday, minutes=180)

    scheduler.generate_schedule()
    ordered = scheduler.sort_by_time()

    assert [t.time for t in ordered] == ["07:15", "12:00", "18:30"]


def test_sort_by_time_does_not_mutate_daily_plan():
    """sort_by_time() returns a new list and leaves the stored plan untouched."""
    a = Task("Late", 10, Priority.HIGH, "Rex", time="20:00")
    b = Task("Early", 10, Priority.HIGH, "Rex", time="06:00")
    owner, pet, scheduler = _owner_with(a, b)

    plan_before = scheduler.generate_schedule()
    original_order = list(plan_before)
    scheduler.sort_by_time()

    assert scheduler.daily_plan == original_order  # unchanged by sorting


def test_generate_schedule_orders_by_priority_then_duration():
    """Highest priority first; among equals, shortest duration first."""
    low = Task("Groom", 10, Priority.LOW, "Rex", time="10:00")
    high_long = Task("Bath", 40, Priority.HIGH, "Rex", time="11:00")
    high_short = Task("Meds", 5, Priority.HIGH, "Rex", time="09:00")
    owner, pet, scheduler = _owner_with(low, high_long, high_short)

    plan = scheduler.generate_schedule()

    # HIGH before LOW; within HIGH, the 5-min task before the 40-min one.
    assert [t.name for t in plan] == ["Meds", "Bath", "Groom"]


# --------------------------------------------------------------------------- #
# 2. Recurrence logic
# --------------------------------------------------------------------------- #
def test_completing_daily_task_spawns_next_day_occurrence():
    """Completing a DAILY task creates a fresh, incomplete task due the next day."""
    med = Task(
        "Give Medication", 5, Priority.HIGH, "Rex",
        time="08:00", frequency=Frequency.DAILY, due_date=date(2026, 7, 7),
    )
    owner, pet, scheduler = _owner_with(med)

    follow_up = scheduler.mark_task_complete(med.id)

    assert follow_up is not None
    assert follow_up.due_date == med.due_date + timedelta(days=1)
    assert follow_up.is_completed is False
    assert follow_up.id != med.id            # brand-new identity
    assert follow_up.time == "08:00"         # same slot preserved
    assert follow_up.frequency == Frequency.DAILY
    assert med.is_completed is True          # original now done
    assert len(pet.tasks) == 2               # original + follow-up


def test_completing_weekly_task_advances_seven_days():
    """A WEEKLY task's follow-up is due seven days later."""
    groom = Task(
        "Grooming", 30, Priority.LOW, "Rex",
        frequency=Frequency.WEEKLY, due_date=date(2026, 7, 7),
    )
    owner, pet, scheduler = _owner_with(groom)

    follow_up = scheduler.mark_task_complete(groom.id)

    assert follow_up.due_date == date(2026, 7, 14)


def test_completing_once_task_spawns_nothing():
    """A one-off (ONCE) task never regenerates."""
    vet = Task("Vet Call", 15, Priority.MEDIUM, "Rex", frequency=Frequency.ONCE)
    owner, pet, scheduler = _owner_with(vet)

    follow_up = scheduler.mark_task_complete(vet.id)

    assert follow_up is None
    assert len(pet.tasks) == 1


def test_double_complete_does_not_spawn_duplicate():
    """Completing an already-complete task returns None and spawns no duplicate."""
    med = Task("Meds", 5, Priority.HIGH, "Rex", frequency=Frequency.DAILY)
    owner, pet, scheduler = _owner_with(med)

    scheduler.mark_task_complete(med.id)
    second = scheduler.mark_task_complete(med.id)

    assert second is None
    assert len(pet.tasks) == 2  # not 3


def test_recurrence_chain_walks_date_forward():
    """Completing a follow-up advances the date again (chains correctly)."""
    med = Task(
        "Meds", 5, Priority.HIGH, "Rex",
        frequency=Frequency.DAILY, due_date=date(2026, 7, 7),
    )
    owner, pet, scheduler = _owner_with(med)

    first = scheduler.mark_task_complete(med.id)
    second = scheduler.mark_task_complete(first.id)

    assert second.due_date == date(2026, 7, 9)  # +2 days total


def test_mark_complete_unknown_id_returns_none():
    """Completing an id that belongs to no pet is a safe no-op."""
    med = Task("Meds", 5, Priority.HIGH, "Rex", frequency=Frequency.DAILY)
    owner, pet, scheduler = _owner_with(med)

    assert scheduler.mark_task_complete("no-such-id") is None
    assert med.is_completed is False


# --------------------------------------------------------------------------- #
# 3. Conflict detection
# --------------------------------------------------------------------------- #
def test_detect_conflicts_flags_duplicate_times():
    """Two tasks at the same start time produce a conflict warning."""
    feed = Task("Feed", 10, Priority.HIGH, "Rex", time="09:05")
    vet = Task("Vet Call", 15, Priority.MEDIUM, "Rex", time="09:05")
    owner, pet, scheduler = _owner_with(feed, vet)

    conflicts = scheduler.detect_conflicts()

    assert len(conflicts) == 1
    assert "09:05" in conflicts[0]


def test_detect_conflicts_empty_when_all_times_distinct():
    """Distinct start times produce no conflicts."""
    a = Task("Feed", 10, Priority.HIGH, "Rex", time="09:00")
    b = Task("Walk", 30, Priority.MEDIUM, "Rex", time="10:00")
    owner, pet, scheduler = _owner_with(a, b)

    assert scheduler.detect_conflicts() == []


def test_detect_conflicts_distinguishes_pets_across_owner():
    """A same-time clash spanning two pets is labelled as multiple pets."""
    owner = Owner("Tester", available_time_minutes=180)
    rex = Pet("Rex", "Golden Retriever", 3)
    milo = Pet("Milo", "Tabby Cat", 5)
    owner.add_pet(rex)
    owner.add_pet(milo)
    rex.add_task(Task("Vet Call", 15, Priority.MEDIUM, "Rex", time="09:05"))
    milo.add_task(Task("Feed", 10, Priority.HIGH, "Milo", time="09:05"))
    scheduler = Scheduler(owner)

    conflicts = scheduler.detect_conflicts()

    assert len(conflicts) == 1
    assert "2 pets" in conflicts[0]


def test_detect_conflicts_ignores_completed_tasks():
    """A completed task no longer counts toward a same-time conflict."""
    feed = Task("Feed", 10, Priority.HIGH, "Rex", time="09:05")
    vet = Task("Vet Call", 15, Priority.MEDIUM, "Rex", time="09:05")
    owner, pet, scheduler = _owner_with(feed, vet)

    scheduler.mark_task_complete(feed.id)  # ONCE task, just flips completion

    assert scheduler.detect_conflicts() == []


# --------------------------------------------------------------------------- #
# 4. Empty / boundary cases
# --------------------------------------------------------------------------- #
def test_schedule_with_no_tasks_is_empty():
    """A pet with no tasks yields an empty plan, no crash."""
    owner, pet, scheduler = _owner_with()

    assert scheduler.generate_schedule() == []
    assert scheduler.sort_by_time() == []


def test_task_exactly_fitting_budget_is_scheduled():
    """A task whose duration equals the remaining budget still fits (<= boundary)."""
    task = Task("Walk", 30, Priority.MEDIUM, "Rex", time="07:00")
    owner, pet, scheduler = _owner_with(task, minutes=30)

    plan = scheduler.generate_schedule()

    assert plan == [task]


def test_task_one_minute_over_budget_is_skipped():
    """A task one minute over the budget is skipped, not scheduled."""
    task = Task("Walk", 31, Priority.MEDIUM, "Rex", time="07:00")
    owner, pet, scheduler = _owner_with(task, minutes=30)

    assert scheduler.generate_schedule() == []


def test_greedy_skip_lets_smaller_lower_priority_task_through():
    """An oversized high-priority task is skipped while a smaller task still fits."""
    big_high = Task("Bath", 60, Priority.HIGH, "Rex", time="09:00")
    small_low = Task("Treat", 5, Priority.LOW, "Rex", time="10:00")
    owner, pet, scheduler = _owner_with(big_high, small_low, minutes=30)

    plan = scheduler.generate_schedule()

    assert big_high not in plan
    assert small_low in plan


def test_completed_tasks_excluded_from_schedule():
    """Already-complete tasks are ignored when building the plan."""
    done = Task("Walk", 30, Priority.HIGH, "Rex", time="07:00")
    pending = Task("Feed", 10, Priority.MEDIUM, "Rex", time="08:00")
    owner, pet, scheduler = _owner_with(done, pending)
    done.mark_complete()

    plan = scheduler.generate_schedule()

    assert plan == [pending]


def test_get_reasoning_before_schedule_returns_sentinel():
    """Asking for reasoning before scheduling returns the not-yet sentinel."""
    owner, pet, scheduler = _owner_with()

    assert scheduler.get_reasoning() == "No schedule has been generated yet."


# --------------------------------------------------------------------------- #
# 5. Input validation
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("bad_time", ["9:05", "25:00", "12:60", "noon", "0905"])
def test_invalid_time_strings_rejected(bad_time):
    """Non zero-padded / out-of-range times raise ValueError."""
    with pytest.raises(ValueError):
        Task("X", 5, Priority.HIGH, "Rex", time=bad_time)


def test_negative_available_time_rejected():
    """An owner cannot be created with a negative time budget."""
    with pytest.raises(ValueError):
        Owner("Tester", available_time_minutes=-1)
