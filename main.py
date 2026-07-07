"""Demo script for the PawPal system.

Builds an owner with two pets and several tasks, generates a schedule,
and prints today's plan to the terminal.
"""

from pawpal_system import Owner, Pet, Task, Priority, Frequency, Scheduler


def build_owner() -> Owner:
    """Create a sample owner with two pets and a handful of tasks."""
    owner = Owner("Stuti", available_time_minutes=90)
    print(f"Created owner '{owner.name}' with a {owner.available_time_minutes} minute budget.")
    
    rex = Pet("Rex", "Golden Retriever", 3)
    milo = Pet("Milo", "Tabby Cat", 5)

    owner.add_pet(rex)
    owner.add_pet(milo)

    # Tasks with different durations, priorities, start times, and frequencies.
    # Added deliberately OUT of chronological order to prove sort_by_time() works.
    rex.add_task(Task("Evening Grooming", duration=45, priority=Priority.LOW, pet_name="Rex", time="18:30", frequency=Frequency.WEEKLY))
    rex.add_task(Task("Give Medication", duration=5, priority=Priority.HIGH, pet_name="Rex", time="08:00", frequency=Frequency.DAILY))
    rex.add_task(Task("Morning Walk", duration=30, priority=Priority.MEDIUM, pet_name="Rex", time="07:15", frequency=Frequency.DAILY))

    milo.add_task(Task("Play / Enrichment", duration=20, priority=Priority.MEDIUM, pet_name="Milo", time="16:45"))
    milo.add_task(Task("Feed", duration=10, priority=Priority.HIGH, pet_name="Milo", time="09:05", frequency=Frequency.DAILY))

    # Deliberate clash: Milo's Feed (09:05) and Rex's Vet Call share 09:05.
    rex.add_task(Task("Vet Call", duration=15, priority=Priority.MEDIUM, pet_name="Rex", time="09:05"))
    return owner


def print_schedule(scheduler: Scheduler) -> None:
    """Print the generated plan as a readable 'Today's Schedule'."""
    scheduler.generate_schedule()
    # Present the plan chronologically, not in the greedy fit-order.
    plan = scheduler.sort_by_time()

    print("=" * 40)
    print("        TODAY'S SCHEDULE (by time)")
    print("=" * 40)

    if not plan:
        print("Nothing scheduled today.")
    else:
        total = 0
        for task in plan:
            total += task.duration
            print(f"{task.time}  {task.name} ({task.pet_name})")
            print(f"        {task.duration} min  |  Priority: {task.priority.name}")
        print("-" * 40)
        print(f"Total scheduled time: {total} min")

    print("\n" + "=" * 40)
    print("        REASONING")
    print("=" * 40)
    print(scheduler.get_reasoning())


def print_filters(owner: Owner) -> None:
    """Demonstrate filter_tasks() by completion status and by pet name."""
    print("\n" + "=" * 40)
    print("        FILTERS")
    print("=" * 40)

    # filter_tasks() only filters; chain sorted() to display chronologically.
    rex_tasks = sorted(owner.filter_tasks(pet_name="Rex"), key=lambda t: t.time)
    print(f"Rex's tasks ({len(rex_tasks)}):")
    for task in rex_tasks:
        print(f"  - {task.name} @ {task.time}")

    pending = owner.filter_tasks(is_completed=False)
    completed = owner.filter_tasks(is_completed=True)
    print(f"Pending: {len(pending)}  |  Completed: {len(completed)}")


def print_conflicts(scheduler: Scheduler) -> None:
    """Print any same-time scheduling conflicts as non-fatal warnings."""
    print("\n" + "=" * 40)
    print("        CONFLICTS")
    print("=" * 40)

    conflicts = scheduler.detect_conflicts()
    if not conflicts:
        print("No scheduling conflicts detected.")
    else:
        for warning in conflicts:
            print(warning)


def print_recurrence(scheduler: Scheduler, owner: Owner) -> None:
    """Complete a DAILY task and show its next occurrence appears automatically."""
    print("\n" + "=" * 40)
    print("        RECURRENCE")
    print("=" * 40)

    med = next(t for t in owner.get_all_tasks() if t.name == "Give Medication")
    before = len(owner.get_all_tasks())
    print(f"Completing daily task '{med.name}' (id ...{med.id[-6:]}).")

    follow_up = scheduler.mark_task_complete(med.id)
    after = len(owner.get_all_tasks())

    print(f"Task count: {before} -> {after}")
    if follow_up is not None:
        print(
            f"Spawned next occurrence: '{follow_up.name}' @ {follow_up.time} "
            f"({follow_up.frequency.value}), completed={follow_up.is_completed}, "
            f"new id ...{follow_up.id[-6:]}"
        )
        print(f"Due date advanced: {med.due_date} -> {follow_up.due_date}")
    print(f"'{med.name}' original now completed={med.is_completed}")


def main() -> None:
    owner = build_owner()

    # Mark one task complete so the completion filter has something to show.
    milo_task = owner.filter_tasks(pet_name="Milo")[0]
    scheduler = Scheduler(owner)
    scheduler.mark_task_complete(milo_task.id)

    scheduler = Scheduler(owner)
    print_schedule(scheduler)
    print_filters(owner)
    print_conflicts(scheduler)
    print_recurrence(scheduler, owner)


if __name__ == "__main__":
    main()
