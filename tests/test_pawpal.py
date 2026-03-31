"""
Basic tests for PawPal+ core logic.
Run with: python -m pytest
"""

import pytest
from pawpal_system import Task, Pet, Owner, Scheduler


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
# Scheduler tests
# ---------------------------------------------------------------------------

def test_schedule_respects_time_window():
    """No scheduled task should end after the owner's day_end."""
    owner = Owner(name="Jordan", day_start="08:00", day_end="08:20")
    pet   = Pet(name="Mochi", species="dog", age=3)
    # 15-min task fits; 30-min task does not
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
