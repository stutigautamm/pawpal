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

Sample test output:

```
# Paste your pytest output here
```

## 📐 Smarter Scheduling

> Fill in once you've implemented scheduling logic.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | Scheduler.sort_by_time() | sorts daily plan chronologically |
| Filtering | Owner.filter_tasks() | filters task list by completion status |
| Conflict handling | Scheduler.detect_conflicts() | groups pending tasks by timeslot |
| Recurring tasks | Task.next_occurrence(), Pet.complete_task(), Scheduler.mark_task_complete() | builds a pending copy of a recurring task advanced to the next due date |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
