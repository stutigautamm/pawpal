"""Demo script for the PawPal system.

Builds an owner with two pets and several tasks, generates a schedule,
and prints today's plan to the terminal.
"""

from pawpal_system import Owner, Pet, Task, Priority, Scheduler


def build_owner() -> Owner:
    """Create a sample owner with two pets and a handful of tasks."""
    owner = Owner("Stuti", available_time_minutes=90)
    print(f"Created owner '{owner.name}' with a {owner.available_time_minutes} minute budget.")
    
    rex = Pet("Rex", "Golden Retriever", 3)
    milo = Pet("Milo", "Tabby Cat", 5)

    owner.add_pet(rex)
    owner.add_pet(milo)

    # Tasks with different durations and priorities.
    rex.add_task(Task("Morning Walk", duration=30, priority=Priority.MEDIUM, pet_name="Rex"))
    rex.add_task(Task("Give Medication", duration=5, priority=Priority.HIGH, pet_name="Rex"))
    rex.add_task(Task("Evening Grooming", duration=45, priority=Priority.LOW, pet_name="Rex"))

    milo.add_task(Task("Feed", duration=10, priority=Priority.HIGH, pet_name="Milo"))
    milo.add_task(Task("Play / Enrichment", duration=20, priority=Priority.MEDIUM, pet_name="Milo"))
    return owner


def print_schedule(scheduler: Scheduler) -> None:
    """Print the generated plan as a readable 'Today's Schedule'."""
    plan = scheduler.generate_schedule()

    print("=" * 40)
    print("        TODAY'S SCHEDULE")
    print("=" * 40)

    if not plan:
        print("Nothing scheduled today.")
    else:
        total = 0
        for i, task in enumerate(plan, start=1):
            total += task.duration
            print(f"{i}. {task.name} ({task.pet_name})")
            print(f"   {task.duration} min  |  Priority: {task.priority.name}")
        print("-" * 40)
        print(f"Total scheduled time: {total} min")

    print("\n" + "=" * 40)
    print("        REASONING")
    print("=" * 40)
    print(scheduler.get_reasoning())


def main() -> None:
    owner = build_owner()
    scheduler = Scheduler(owner)
    print_schedule(scheduler)


if __name__ == "__main__":
    main()
