"""
Tests for PawPal+ core logic.
Run with: python3 -m pytest
"""

import pytest
from datetime import date, timedelta
from pawpal_system import Task, Pet, Owner, Scheduler, ScheduledTask


# ---------------------------------------------------------------------------
# Task tests
# ---------------------------------------------------------------------------

def test_mark_complete_changes_status():
    """mark_complete() should flip completed from False to True."""
    task = Task(title="Morning walk", duration_minutes=30, priority="high")
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_mark_complete_is_idempotent():
    """Calling mark_complete() twice should leave completed as True."""
    task = Task(title="Feed", duration_minutes=10, priority="medium")
    task.mark_complete()
    task.mark_complete()
    assert task.completed is True


def test_mark_complete_once_returns_none():
    """A one-off task should not spawn a successor."""
    task = Task(title="Vet visit", duration_minutes=60, priority="high", frequency="once")
    assert task.mark_complete() is None


def test_mark_complete_daily_returns_next_task():
    """A daily task should return a new Task due one day later."""
    today = date.today()
    task = Task(title="Feed", duration_minutes=10, priority="high",
                frequency="daily", due_date=today)
    next_task = task.mark_complete()
    assert next_task is not None
    assert next_task.completed is False
    assert next_task.due_date == today + timedelta(days=1)
    assert next_task.frequency == "daily"
    assert next_task.title == task.title


def test_mark_complete_weekly_returns_next_task():
    """A weekly task should return a new Task due seven days later."""
    today = date.today()
    task = Task(title="Bath", duration_minutes=20, priority="medium",
                frequency="weekly", due_date=today)
    next_task = task.mark_complete()
    assert next_task is not None
    assert next_task.due_date == today + timedelta(weeks=1)


# ---------------------------------------------------------------------------
# Pet tests
# ---------------------------------------------------------------------------

def test_add_task_increases_pet_task_count():
    """Each call to add_task() should grow the pet's task list by one."""
    pet = Pet(name="Mochi", species="dog", age=3)
    assert len(pet.get_tasks()) == 0
    pet.add_task(Task(title="Walk",  duration_minutes=20, priority="high"))
    assert len(pet.get_tasks()) == 1
    pet.add_task(Task(title="Feed",  duration_minutes=10, priority="medium"))
    assert len(pet.get_tasks()) == 2


def test_get_tasks_returns_copy():
    """Mutating the returned list should not affect the pet's internal list."""
    pet = Pet(name="Luna", species="cat", age=5)
    pet.add_task(Task(title="Brushing", duration_minutes=15, priority="low"))
    tasks = pet.get_tasks()
    tasks.clear()
    assert len(pet.get_tasks()) == 1


# ---------------------------------------------------------------------------
# Owner tests
# ---------------------------------------------------------------------------

def test_add_pet_increases_pet_count():
    """add_pet() should register the pet with the owner."""
    owner = Owner(name="Jordan")
    assert len(owner.get_pets()) == 0
    owner.add_pet(Pet(name="Mochi", species="dog", age=3))
    assert len(owner.get_pets()) == 1


def test_remove_pet_by_name():
    """remove_pet() should drop only the pet with the matching name."""
    owner = Owner(name="Jordan")
    owner.add_pet(Pet(name="Mochi", species="dog", age=3))
    owner.add_pet(Pet(name="Luna",  species="cat", age=5))
    owner.remove_pet("Mochi")
    names = [p.name for p in owner.get_pets()]
    assert "Mochi" not in names
    assert "Luna"  in names


# ---------------------------------------------------------------------------
# Scheduler — core
# ---------------------------------------------------------------------------

def test_schedule_respects_time_window():
    """No scheduled task should end after the owner's day_end."""
    owner = Owner(name="Jordan", day_start="08:00", day_end="08:20")
    pet   = Pet(name="Mochi", species="dog", age=3)
    pet.add_task(Task(title="Feed",  duration_minutes=15, priority="high"))
    pet.add_task(Task(title="Walk",  duration_minutes=30, priority="high"))
    owner.add_pet(pet)
    schedule = Scheduler(owner).build_schedule()
    assert len(schedule) == 1
    assert schedule[0].task.title == "Feed"


def test_high_priority_scheduled_before_low():
    """High-priority tasks should appear earlier in the schedule than low ones."""
    owner = Owner(name="Jordan", day_start="08:00", day_end="20:00")
    pet   = Pet(name="Mochi", species="dog", age=3)
    pet.add_task(Task(title="Nap",   duration_minutes=10, priority="low"))
    pet.add_task(Task(title="Walk",  duration_minutes=10, priority="high"))
    owner.add_pet(pet)
    schedule = Scheduler(owner).build_schedule()
    assert schedule[0].task.title == "Walk"


def test_completed_tasks_excluded_from_schedule():
    """Tasks already marked complete should not appear in build_schedule."""
    owner = Owner(name="Jordan", day_start="08:00", day_end="20:00")
    pet   = Pet(name="Mochi", species="dog", age=3)
    done  = Task(title="Walk",  duration_minutes=20, priority="high", completed=True)
    todo  = Task(title="Feed",  duration_minutes=10, priority="medium")
    pet.add_task(done)
    pet.add_task(todo)
    owner.add_pet(pet)
    schedule = Scheduler(owner).build_schedule()
    titles = [st.task.title for st in schedule]
    assert "Walk" not in titles
    assert "Feed" in titles


# ---------------------------------------------------------------------------
# Scheduler — edge cases
# ---------------------------------------------------------------------------

def test_schedule_owner_with_no_pets():
    """An owner with no pets should produce an empty schedule without error."""
    owner = Owner(name="Jordan", day_start="08:00", day_end="20:00")
    assert Scheduler(owner).build_schedule() == []


def test_schedule_pet_with_no_tasks():
    """A pet with no tasks should not cause errors; other pets still schedule."""
    owner = Owner(name="Jordan", day_start="08:00", day_end="20:00")
    empty = Pet(name="Ghost", species="cat", age=2)          # no tasks
    mochi = Pet(name="Mochi", species="dog", age=3)
    mochi.add_task(Task(title="Walk", duration_minutes=20, priority="high"))
    owner.add_pet(empty)
    owner.add_pet(mochi)
    schedule = Scheduler(owner).build_schedule()
    assert len(schedule) == 1
    assert schedule[0].pet_name == "Mochi"


def test_schedule_all_tasks_already_done():
    """When every task is completed, build_schedule should return an empty list."""
    owner = Owner(name="Jordan", day_start="08:00", day_end="20:00")
    pet   = Pet(name="Mochi", species="dog", age=3)
    pet.add_task(Task(title="Walk", duration_minutes=20, priority="high", completed=True))
    pet.add_task(Task(title="Feed", duration_minutes=10, priority="medium", completed=True))
    owner.add_pet(pet)
    assert Scheduler(owner).build_schedule() == []


# ---------------------------------------------------------------------------
# Scheduler — sort_by_time
# ---------------------------------------------------------------------------

def test_sort_by_time_orders_ascending():
    """sort_by_time should reorder ScheduledTask objects by start_time."""
    owner = Owner(name="Jordan")
    sched = Scheduler(owner)
    task  = Task(title="X", duration_minutes=5, priority="low")
    slots = [
        ScheduledTask(task=task, pet_name="A", start_time="10:00", end_time="10:05"),
        ScheduledTask(task=task, pet_name="B", start_time="08:00", end_time="08:05"),
        ScheduledTask(task=task, pet_name="C", start_time="09:00", end_time="09:05"),
    ]
    result = sched.sort_by_time(slots)
    assert [s.start_time for s in result] == ["08:00", "09:00", "10:00"]


def test_sort_by_time_empty_list():
    """sort_by_time on an empty list should return an empty list without error."""
    owner = Owner(name="Jordan")
    assert Scheduler(owner).sort_by_time([]) == []


# ---------------------------------------------------------------------------
# Scheduler — filter_tasks
# ---------------------------------------------------------------------------

def test_filter_by_pet_name():
    """filter_tasks(pet_name=...) should return only that pet's tasks."""
    owner = Owner(name="Jordan", day_start="08:00", day_end="20:00")
    mochi = Pet(name="Mochi", species="dog", age=3)
    luna  = Pet(name="Luna",  species="cat", age=5)
    mochi.add_task(Task(title="Walk", duration_minutes=20, priority="high"))
    luna.add_task(Task(title="Feed",  duration_minutes=5,  priority="high"))
    owner.add_pet(mochi)
    owner.add_pet(luna)

    results = Scheduler(owner).filter_tasks(pet_name="Mochi")
    assert all(name == "Mochi" for name, _ in results)
    assert len(results) == 1


def test_filter_by_completion_status():
    """filter_tasks(completed=False) should exclude completed tasks."""
    owner = Owner(name="Jordan", day_start="08:00", day_end="20:00")
    pet   = Pet(name="Mochi", species="dog", age=3)
    done  = Task(title="Walk", duration_minutes=20, priority="high", completed=True)
    todo  = Task(title="Feed", duration_minutes=10, priority="medium")
    pet.add_task(done)
    pet.add_task(todo)
    owner.add_pet(pet)

    results = Scheduler(owner).filter_tasks(completed=False)
    titles = [t.title for _, t in results]
    assert "Walk" not in titles
    assert "Feed" in titles


def test_filter_combined_pet_and_status():
    """filter_tasks with both pet_name and completed should apply both filters."""
    owner = Owner(name="Jordan", day_start="08:00", day_end="20:00")
    mochi = Pet(name="Mochi", species="dog", age=3)
    luna  = Pet(name="Luna",  species="cat", age=5)
    mochi.add_task(Task(title="Walk", duration_minutes=20, priority="high", completed=True))
    mochi.add_task(Task(title="Feed", duration_minutes=10, priority="medium"))
    luna.add_task(Task(title="Feed",  duration_minutes=5,  priority="high"))
    owner.add_pet(mochi)
    owner.add_pet(luna)

    # Only Mochi's incomplete tasks
    results = Scheduler(owner).filter_tasks(pet_name="Mochi", completed=False)
    assert len(results) == 1
    assert results[0][1].title == "Feed"
    assert all(name == "Mochi" for name, _ in results)


# ---------------------------------------------------------------------------
# Scheduler — complete_task (recurring)
# ---------------------------------------------------------------------------

def test_complete_task_recurring_adds_to_pet():
    """complete_task on a daily task should append a new task to the pet."""
    owner = Owner(name="Jordan", day_start="08:00", day_end="20:00")
    pet   = Pet(name="Mochi", species="dog", age=3)
    task  = Task(title="Feed", duration_minutes=10, priority="high", frequency="daily")
    pet.add_task(task)
    owner.add_pet(pet)

    initial_count = len(pet.get_tasks())
    Scheduler(owner).complete_task(pet, task)
    assert len(pet.get_tasks()) == initial_count + 1
    assert pet.get_tasks()[-1].completed is False


def test_complete_task_once_does_not_add():
    """complete_task on a one-off task should NOT append a new task."""
    owner = Owner(name="Jordan", day_start="08:00", day_end="20:00")
    pet   = Pet(name="Mochi", species="dog", age=3)
    task  = Task(title="Vet visit", duration_minutes=60, priority="high", frequency="once")
    pet.add_task(task)
    owner.add_pet(pet)

    initial_count = len(pet.get_tasks())
    Scheduler(owner).complete_task(pet, task)
    assert len(pet.get_tasks()) == initial_count


# ---------------------------------------------------------------------------
# Scheduler — detect_conflicts
# ---------------------------------------------------------------------------

def test_detect_conflicts_finds_overlap():
    """Two overlapping time slots should produce a warning."""
    owner = Owner(name="Jordan")
    sched = Scheduler(owner)
    task  = Task(title="X", duration_minutes=10, priority="high")
    slots = [
        ScheduledTask(task=task, pet_name="A", start_time="08:00", end_time="08:30"),
        ScheduledTask(task=task, pet_name="B", start_time="08:15", end_time="08:25"),
    ]
    warnings = sched.detect_conflicts(slots)
    assert len(warnings) == 1
    assert "WARNING" in warnings[0]


def test_detect_conflicts_no_overlap():
    """Back-to-back (non-overlapping) tasks should produce no warnings."""
    owner = Owner(name="Jordan")
    sched = Scheduler(owner)
    task  = Task(title="X", duration_minutes=10, priority="high")
    slots = [
        ScheduledTask(task=task, pet_name="A", start_time="08:00", end_time="08:30"),
        ScheduledTask(task=task, pet_name="B", start_time="08:30", end_time="08:40"),
    ]
    assert sched.detect_conflicts(slots) == []


def test_detect_conflicts_exact_same_start_time():
    """Two tasks starting at the same time are an overlap and must be flagged."""
    owner = Owner(name="Jordan")
    sched = Scheduler(owner)
    task  = Task(title="X", duration_minutes=10, priority="high")
    slots = [
        ScheduledTask(task=task, pet_name="A", start_time="08:00", end_time="08:10"),
        ScheduledTask(task=task, pet_name="B", start_time="08:00", end_time="08:10"),
    ]
    warnings = sched.detect_conflicts(slots)
    assert len(warnings) == 1


def test_detect_conflicts_single_task():
    """A schedule with one task has no pairs to compare; no warnings expected."""
    owner = Owner(name="Jordan")
    sched = Scheduler(owner)
    task  = Task(title="X", duration_minutes=10, priority="high")
    slots = [ScheduledTask(task=task, pet_name="A", start_time="08:00", end_time="08:10")]
    assert sched.detect_conflicts(slots) == []


def test_detect_conflicts_clean_auto_schedule():
    """The auto-generated schedule should never have conflicts."""
    owner = Owner(name="Jordan", day_start="08:00", day_end="20:00")
    pet   = Pet(name="Mochi", species="dog", age=3)
    pet.add_task(Task(title="Walk", duration_minutes=20, priority="high"))
    pet.add_task(Task(title="Feed", duration_minutes=10, priority="medium"))
    owner.add_pet(pet)
    sched    = Scheduler(owner)
    schedule = sched.build_schedule()
    assert sched.detect_conflicts(schedule) == []
