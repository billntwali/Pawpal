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

## Features

- **Priority-based scheduling** — required tasks always come before optional ones; within each group, high → medium → low priority tasks are scheduled first
- **Time-window enforcement** — the scheduler respects the owner's `day_start` / `day_end`; no task is ever truncated or allowed to run over
- **Sorting by time** — any generated schedule can be re-displayed in chronological order using a `lambda` key on `HH:MM` strings
- **Filtering** — browse tasks by pet name, completion status, or both combined
- **Recurring tasks** — tasks marked `daily` or `weekly` automatically queue their next occurrence when marked complete, using `timedelta` to calculate the correct due date
- **Conflict detection** — the scheduler scans every pair of scheduled tasks for overlapping time windows and surfaces human-readable warnings rather than crashing
- **Mark complete in UI** — each scheduled task has a "Mark done" button; recurring tasks show a success message with the next due date

## 📸 Demo

<a href="/course_images/ai110/pawpal_screenshot.png" target="_blank"><img src='/course_images/ai110/pawpal_screenshot.png' title='PawPal App' width='' alt='PawPal App' class='center-block' /></a>

## Smarter Scheduling

PawPal+ goes beyond a simple task list with four algorithmic features:

| Feature | How it works |
|---------|-------------|
| **Sorting** | `Scheduler.sort_by_time()` reorders any schedule by clock time using a `lambda` key on `HH:MM` strings, which sort correctly without parsing. |
| **Filtering** | `Scheduler.filter_tasks(pet_name, completed)` returns `(pet_name, Task)` pairs across all pets, with optional filters for which pet and whether tasks are done or pending. |
| **Recurring tasks** | `Task` has a `frequency` field (`"once"`, `"daily"`, `"weekly"`). Calling `Scheduler.complete_task(pet, task)` marks it done and, if recurring, automatically appends the next occurrence (via `timedelta`) to the pet's task list. |
| **Conflict detection** | `Scheduler.detect_conflicts(schedule)` checks every pair of scheduled tasks for overlapping time windows and returns human-readable warnings rather than crashing. |

## Testing PawPal+

Run the full test suite from the project root:

```bash
python3 -m pytest
```

The suite contains **27 tests** across five areas:

| Area | What is tested |
|------|---------------|
| **Task lifecycle** | `mark_complete()` flips status; one-off tasks return `None`; daily/weekly tasks return a correctly dated successor |
| **Pet management** | `add_task()` grows the list; `get_tasks()` returns a copy so callers can't corrupt internal state |
| **Owner management** | `add_pet()` / `remove_pet()` add and drop by name correctly |
| **Scheduler — core** | Priority ordering, time-window enforcement, exclusion of completed tasks, empty-pet and no-pet edge cases |
| **Algorithms** | Sorting by time (including empty list); filtering by pet name, status, and both combined; recurring-task auto-spawn; conflict detection for overlapping, back-to-back, same-start, single-task, and clean auto-generated schedules |

**Confidence level: ★★★★☆ (4/5)**
All 27 tests pass with zero warnings. The main untested gap is invalid input (e.g. malformed `HH:MM` strings or negative durations) — those are the next edge cases to cover.

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
