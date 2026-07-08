# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

```
# e.g.:
# Daily plan for Biscuit (Golden Retriever):
#   08:00 — Morning walk (30 min) [priority: high]
#   09:00 — Feeding (10 min) [priority: high]
#   ...

Created owner 'Stuti' with a 90 minute budget.
========================================
        TODAY'S SCHEDULE (by time)
========================================
07:15  Morning Walk (Rex)
        30 min  |  Priority: MEDIUM
08:00  Give Medication (Rex)
        5 min  |  Priority: HIGH
09:05  Feed (Milo)
        10 min  |  Priority: HIGH
09:05  Vet Call (Rex)
        15 min  |  Priority: MEDIUM
----------------------------------------
Total scheduled time: 60 min

========================================
        REASONING
========================================
Starting schedule for Stuti with 90 min available.
Scheduled 'Give Medication' for Rex (HIGH, 5 min). 85 min left.
Scheduled 'Feed' for Milo (HIGH, 10 min). 75 min left.
Scheduled 'Vet Call' for Rex (MEDIUM, 15 min). 60 min left.
Scheduled 'Morning Walk' for Rex (MEDIUM, 30 min). 30 min left.
Skipped 'Evening Grooming' for Rex (LOW, 45 min) ▒ needs 45 min but only 30 left.
Final plan: 4 of 5 pending task(s), 60 of 90 min used.
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```
Using the command python -m pytest to run the tests, here is a description of what the tests cover:

1. Sorting and Urgency: Makes sure tasks are ordered by importance. If importance is equal, shorter tasks come first. The final plan is sorted perfectly from morning to night.
2. Repeating Tasks: Confirms that completing a daily or weekly task automatically creates a brand-new copy for the next due date without making accidental duplicates.
3. Time Conflicts: Checks for tasks set for the exact same time and displays a clear warning for single or multiple pets while ignoring tasks that are already done.
4. Limits and Budget: Tests that tasks fitting the minute budget perfectly are scheduled, while tasks that take too long are skipped safely.
5. Data Protection: Makes sure time entries use the correct format (like 09:05) and stops errors like typing in a negative time budget.


Sample test output:

```
# Paste your pytest output here
============================= test session starts =============================
platform win32 -- Python 3.13.12, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Stuti\AI110\pawpal
plugins: anyio-4.14.1
collected 27 items

tests\test_pawpal.py ...........................                         [100%]

============================= 27 passed in 0.07s ==============================
```
System Reliability Rating
(5/5 Stars)
Since all the tests, which include edge cases and happy paths, are passing perfectly, the core engine proves to be completely reliable at tracking dates, catch errors, and scheduling tasks correctly.

## 📐 Smarter Scheduling

> Fill in once you've implemented scheduling logic.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | Scheduler.sort_by_time() | sorts daily plan chronologically |
| Filtering | Owner.filter_tasks() | filters task list by completion status |
| Conflict handling | Scheduler.detect_conflicts() | groups pending tasks by timeslot |
| Recurring tasks | Task.next_occurrence(), Pet.complete_task(), Scheduler.mark_task_complete() | builds a pending copy of a recurring task advanced to the next due date |

## 📸 Demo Walkthrough

Main UI Features and User Actions

Owner Profile Setup: Configure owner name and update available time budget dynamically.
Pet Registry: Input a pet profile with its name, species/breed, and age parameters.
Task Formulation: Add tasks featuring title, runtime, zero-padded HH:MM target time, explicit priority status, and frequency recurrences.
Status Updates: Dropdown menus allow items to be logged as completed on the fly.
Schedule Compilation: Triggering the engine displays an orderly, timed task matrix and expands the scheduler logic thought logs.


Describe your app in numbered steps so a reader can follow along without watching a video:

1. Create the Owner Profile: Type in the owner's name as your name and set the available care time to `90` minutes.
2. Add Your Pets: Go to the "Add a Pet" form. Go to the "Add a Pet" section. Type `"Rex"`, choose `"dog"`, set the age to `3`, and click the button. Do this again to add `"Milo"` (species: `"cat"`, age: `5`).
3. Create the Task Lists: Use the "Add a Task" form to assign multiple items. For example, add a `"Morning Walk"` for Rex (30 min, Medium priority, at `07:15`, daily) and a `"Feed"` task for Milo (10 min, High priority, at `09:05`, Daily).
4. Look for Warnings: Look at the tasks list. If you accidentally schedule two different tasks at the exact same time, a warning banner will pop up to alert you.
5. Generate and Review the Schedule: Scroll to the bottom and click "Generate schedule". The app will instantly show your daily routine sorted from morning to night, along with the reaosning explaining how it fit everything into your 90-minute limit.


Fenced code block of sample CLI output from running main.py
```
Created owner 'Stuti' with a 90 minute budget.
========================================
        TODAY'S SCHEDULE (by time)
========================================
07:15  Morning Walk (Rex)
        30 min  |  Priority: MEDIUM
08:00  Give Medication (Rex)
        5 min  |  Priority: HIGH
09:05  Feed (Milo)
        10 min  |  Priority: HIGH
09:05  Vet Call (Rex)
        15 min  |  Priority: MEDIUM
----------------------------------------
Total scheduled time: 60 min

========================================
        REASONING
========================================
Starting schedule for Stuti with 90 min available.
Ignored 1 already-completed task(s).
Scheduled 'Give Medication' for Rex (HIGH, 5 min). 85 min left.
Scheduled 'Feed' for Milo (HIGH, 10 min). 75 min left.
Scheduled 'Vet Call' for Rex (MEDIUM, 15 min). 60 min left.
Scheduled 'Morning Walk' for Rex (MEDIUM, 30 min). 30 min left.
Skipped 'Evening Grooming' for Rex (LOW, 45 min) ▒ needs 45 min but only 30 left.
Final plan: 4 of 5 pending task(s), 60 of 90 min used.

========================================
        FILTERS
========================================
Rex's tasks (4):
  - Morning Walk @ 07:15
  - Give Medication @ 08:00
  - Vet Call @ 09:05
  - Evening Grooming @ 18:30
Pending: 5  |  Completed: 1

========================================
        CONFLICTS
========================================
WARNING - Conflict at 09:05: 2 tasks (2 pets) - 'Vet Call' (Rex), 'Feed' (Milo).

========================================
        RECURRENCE
========================================
Completing daily task 'Give Medication' (id ...302b17).
Task count: 6 -> 7
Spawned next occurrence: 'Give Medication' @ 08:00 (daily), completed=False, new id ...e67fc1
Due date advanced: 2026-07-07 -> 2026-07-08
'Give Medication' original now completed=True
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
