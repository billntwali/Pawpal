# 🐾 PawPal+

> A smart daily pet care planner built with Python and Streamlit. PawPal+ helps pet owners schedule care tasks across multiple pets, detect scheduling conflicts, and automatically manage recurring routines — all through a clean, interactive UI.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.x-red?logo=streamlit&logoColor=white)
![Pytest](https://img.shields.io/badge/Tests-27%20passing-brightgreen?logo=pytest&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

---

## 📸 Demo

<a href="/course_images/ai110/pawpal_screenshot.png" target="_blank"><img src='/course_images/ai110/pawpal_screenshot.png' title='PawPal App' width='' alt='PawPal App' class='center-block' /></a>

---

## Overview

PawPal+ solves a real problem: busy pet owners managing multiple pets, each with different feeding schedules, walks, medications, and grooming needs. Rather than relying on a static to-do list, PawPal+ applies a priority-based scheduling algorithm that fits tasks into the owner's available hours, warns about conflicts, and rolls over recurring tasks automatically.

The project was built using an **OOP-first, UI-last** methodology — the domain model and scheduling logic were fully designed (UML), implemented, and tested in pure Python before any UI code was written. This separation means the logic layer is independently testable and reusable.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.10+ |
| UI framework | Streamlit |
| Data modelling | Python `dataclasses` |
| Date arithmetic | `datetime.timedelta` |
| Testing | `pytest` |
| Diagram | Mermaid.js |

---

## Features

### Scheduling Engine
- **Priority-based scheduling** — required tasks are always scheduled before optional ones; within each group, tasks are ordered high → medium → low priority
- **Time-window enforcement** — every task must fit within the owner's `day_start` / `day_end` window; tasks that would run over are skipped, never truncated
- **Recurring tasks** — tasks can be set to `once`, `daily`, or `weekly`; marking one complete automatically queues the next occurrence with the correct due date via `timedelta`
- **Conflict detection** — scans every pair of scheduled tasks for overlapping time windows using interval logic (`A.start < B.end AND B.start < A.end`); surfaces human-readable warnings instead of crashing

### Data & Filtering
- **Sort by time** — switch any generated schedule between priority order and chronological order
- **Filter view** — browse tasks across all pets filtered by pet name, completion status, or both combined
- **Defensive copies** — `get_tasks()` and `get_pets()` return copies so UI code cannot corrupt the internal domain model

### UI (Streamlit)
- **Three-tab layout** — Pets & Tasks, Today's Schedule, Browse & Filter
- **Persistent state** — `st.session_state` keeps the `Owner` object alive across reruns without re-initialising data on every interaction
- **Mark done in-app** — each scheduled task has a "Mark done" button; recurring tasks display the next due date on completion
- **Conflict warnings** — `st.warning` banners appear inline for any detected scheduling conflicts; `st.success` confirms a clean schedule

---

## Architecture

```
pawpal_system.py         ← Pure Python logic layer (no UI dependencies)
├── Task (dataclass)     ← A single care activity
├── ScheduledTask        ← A Task placed on the timeline (with pet_name, start/end)
├── Pet                  ← Owns a list of Tasks
├── Owner                ← Owns a list of Pets, defines daily availability
└── Scheduler            ← Orchestrates scheduling, sorting, filtering, conflict detection

app.py                   ← Streamlit UI layer (imports from pawpal_system)
tests/
└── test_pawpal.py       ← 27 pytest tests (unit + edge cases)
```

**Class relationships:**
`Owner` → (1 to many) → `Pet` → (1 to many) → `Task`
`Scheduler` takes an `Owner` and produces a list of `ScheduledTask` objects.

The full Mermaid class diagram is in [uml_final.md](uml_final.md).

---

## Getting Started

### Prerequisites

- Python 3.10 or higher
- `pip`

### Installation

```bash
git clone https://github.com/<your-username>/pawpal-plus.git
cd pawpal-plus
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Run the app

```bash
streamlit run app.py
```

The app opens at `http://localhost:8501`.

### Run the demo script (terminal only)

```bash
python3 main.py
```

Outputs a full schedule, filtered views, recurring task demo, and conflict detection to stdout.

---

## Tests

```bash
python3 -m pytest
```

27 tests covering:

| Area | What is verified |
|------|-----------------|
| Task lifecycle | `mark_complete()` status change; one-off returns `None`; daily/weekly returns a correctly dated successor |
| Pet management | `add_task()` grows the list; `get_tasks()` returns a defensive copy |
| Owner management | `add_pet()` / `remove_pet()` register and drop correctly |
| Scheduler core | Priority order, time-window enforcement, completed-task exclusion, empty-owner/empty-pet edge cases |
| Algorithms | `sort_by_time` (including empty input); `filter_tasks` by name, status, and combined; recurring auto-spawn; conflict detection for overlap, back-to-back, same start time, single task, and clean generated schedules |

**Test confidence: ★★★★☆** — all 27 pass. Known gap: no validation tests for malformed `HH:MM` input or negative durations.

---

## Project Structure

```
.
├── app.py                  # Streamlit UI
├── pawpal_system.py        # Domain model + scheduler logic
├── main.py                 # Terminal demo script
├── tests/
│   └── test_pawpal.py      # pytest suite (27 tests)
├── uml_final.md            # Final Mermaid class diagram + change log
├── reflection.md           # Design decisions, tradeoffs, AI collaboration notes
├── requirements.txt
└── README.md
```

---

## Design Decisions

- **Dataclasses for `Task` and `ScheduledTask`** — these are pure data containers with no business logic beyond `mark_complete()`; dataclasses eliminate boilerplate and make field declarations self-documenting.
- **`ScheduledTask` holds `pet_name` directly** — avoids a reverse lookup when generating the human-readable schedule explanation across multiple pets.
- **String comparison for conflict detection** — zero-padded `HH:MM` strings compare correctly as plain strings in Python, so `datetime` parsing is unnecessary overhead.
- **`get_tasks()` returns a copy** — the UI layer receives a snapshot; mutations to that list don't affect the pet's internal state.

Full design rationale and tradeoffs are documented in [reflection.md](reflection.md).

---

## License

MIT
