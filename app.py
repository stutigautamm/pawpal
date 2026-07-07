import streamlit as st
from pawpal_system import Owner, Pet, Task, Priority, Frequency, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")


def get_owner() -> Owner:
    """Return the session's Owner, creating it once if it doesn't exist yet.

    st.session_state is the 'vault' that persists across reruns and page
    navigation. Every widget interaction re-runs this script top to bottom,
    so we only build a new Owner when one isn't already stored.
    """
    if "owner" not in st.session_state:
        st.session_state.owner = Owner(name="Jordan", available_time_minutes=180)
    return st.session_state.owner


owner = get_owner()

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

# Maps the UI's priority labels to the Priority enum from pawpal_system.
PRIORITY_MAP = {"low": Priority.LOW, "medium": Priority.MEDIUM, "high": Priority.HIGH}
# Maps the UI's frequency labels to the Frequency enum from pawpal_system.
FREQUENCY_MAP = {
    "once": Frequency.ONCE,
    "daily": Frequency.DAILY,
    "weekly": Frequency.WEEKLY,
}

st.divider()

# --- Owner settings -------------------------------------------------------
st.subheader("Owner")
owner.name = st.text_input("Owner name", value=owner.name)
owner.update_availability(
    st.number_input(
        "Available time today (minutes)",
        min_value=0,
        max_value=1440,
        value=owner.available_time_minutes,
    )
)

st.divider()

# --- Add a Pet ------------------------------------------------------------
st.subheader("Add a Pet")
col1, col2, col3 = st.columns(3)
with col1:
    new_pet_name = st.text_input("Pet name", value="Mochi")
with col2:
    new_pet_breed = st.selectbox("Species / breed", ["dog", "cat", "other"])
with col3:
    new_pet_age = st.number_input("Age", min_value=0, max_value=50, value=2)

if st.button("Add pet"):
    if any(p.name == new_pet_name for p in owner.pets):
        st.warning(f"A pet named '{new_pet_name}' already exists.")
    else:
        owner.add_pet(Pet(name=new_pet_name, breed=new_pet_breed, age=int(new_pet_age)))
        st.success(f"Added {new_pet_name}.")

st.divider()

# --- Add a Task to a Pet --------------------------------------------------
st.subheader("Add a Task")
if not owner.pets:
    st.info("Add a pet first, then you can assign tasks to it.")
else:
    target_pet_name = st.selectbox("For which pet?", [p.name for p in owner.pets])

    col1, col2 = st.columns(2)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
    with col2:
        task_time = st.text_input("Start time (HH:MM)", value="08:00")

    col3, col4, col5 = st.columns(3)
    with col3:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    with col4:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
    with col5:
        frequency = st.selectbox("Frequency", ["once", "daily", "weekly"], index=0)

    if st.button("Add task"):
        target_pet = next(p for p in owner.pets if p.name == target_pet_name)
        try:
            target_pet.add_task(
                Task(
                    name=task_title,
                    duration=int(duration),
                    priority=PRIORITY_MAP[priority],
                    pet_name=target_pet.name,
                    time=task_time,
                    frequency=FREQUENCY_MAP[frequency],
                )
            )
            st.success(f"Added '{task_title}' to {target_pet_name}.")
        except ValueError as err:
            st.error(str(err))

# --- Current pets & tasks -------------------------------------------------
if owner.pets:
    st.markdown("### Current pets & tasks")
    for pet in owner.pets:
        st.markdown(f"**{pet.name}** ({pet.breed}, age {pet.age}) — {pet.get_total_task_duration()} min total")
        if pet.tasks:
            st.table(
                [
                    {
                        "due": t.due_date.isoformat(),
                        "time": t.time,
                        "task": t.name,
                        "minutes": t.duration,
                        "priority": t.priority.name,
                        "frequency": t.frequency.value,
                        "done": t.is_completed,
                    }
                    for t in sorted(pet.tasks, key=lambda t: t.time)
                ]
            )
        else:
            st.caption("No tasks yet.")

st.divider()

# --- Mark a Task Complete -------------------------------------------------
st.subheader("Mark a Task Complete")
st.caption("Completing a daily/weekly task automatically schedules its next occurrence.")

pending = owner.filter_tasks(is_completed=False)
if not pending:
    st.info("No pending tasks to complete.")
else:
    # Map a readable label back to each task id so we can act on the selection.
    label_to_id = {
        f"{t.time}  {t.name} ({t.pet_name}) · {t.frequency.value}": t.id
        for t in sorted(pending, key=lambda t: t.time)
    }
    choice = st.selectbox("Which task did you finish?", list(label_to_id))

    if st.button("Mark complete"):
        scheduler = Scheduler(owner)
        follow_up = scheduler.mark_task_complete(label_to_id[choice])
        if follow_up is not None:
            st.success(
                f"Done! Scheduled the next {follow_up.frequency.value} occurrence "
                f"of '{follow_up.name}' on {follow_up.due_date.isoformat()} at {follow_up.time}."
            )
        else:
            st.success("Marked complete. (One-off task — no recurrence.)")

st.divider()

# --- Build Schedule -------------------------------------------------------
st.subheader("Build Schedule")

if st.button("Generate schedule"):
    scheduler = Scheduler(owner)
    plan = scheduler.generate_schedule()

    if not plan:
        st.info("Nothing could be scheduled.")
    else:
        st.markdown("#### Today's Schedule")
        total = 0
        for i, task in enumerate(plan, start=1):
            total += task.duration
            st.write(f"{i}. **{task.name}** ({task.pet_name}) — {task.duration} min · {task.priority.name}")
        st.caption(f"Total scheduled time: {total} of {owner.available_time_minutes} min")

    with st.expander("Why this plan? (reasoning)"):
        st.text(scheduler.get_reasoning())
