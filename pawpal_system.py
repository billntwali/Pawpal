"""
PawPal+ — backend logic layer.
All classes representing the domain model and scheduling live here.
"""

from dataclasses import dataclass
from typing import Optional


# ---------------------------------------------------------------------------
# Data-only objects (dataclasses)
# ---------------------------------------------------------------------------

@dataclass
class Task:
    """A single pet-care activity that can be scheduled."""
    title: str
    duration_minutes: int
    priority: str          # "low" | "medium" | "high"
    time_of_day: Optional[str] = None  # "morning" | "afternoon" | "evening" | None
    is_required: bool = True


@dataclass
class ScheduledTask:
    """A Task that has been placed on the day's timeline."""
    task: Task
    pet_name: str          # which pet this task is for
    start_time: str        # e.g. "08:00"
    end_time: str          # e.g. "08:20"
    reason: str = ""       # why this task was chosen / placed here


# ---------------------------------------------------------------------------
# Domain objects
# ---------------------------------------------------------------------------

class Pet:
    """Represents a pet owned by an Owner."""

    def __init__(
        self,
        name: str,
        species: str,
        age: int,
        breed: str = "",
        special_needs: Optional[list[str]] = None,
    ) -> None:
        self.name = name
        self.species = species
        self.age = age
        self.breed = breed
        self.special_needs: list[str] = special_needs or []
        self._tasks: list[Task] = []

    def add_task(self, task: Task) -> None:
        """Attach a care task to this pet."""
        pass  # TODO: implement

    def get_tasks(self) -> list[Task]:
        """Return all tasks associated with this pet."""
        pass  # TODO: implement


class Owner:
    """Represents the pet owner and their daily availability."""

    def __init__(
        self,
        name: str,
        email: str = "",
        day_start: str = "07:00",
        day_end: str = "21:00",
    ) -> None:
        self.name = name
        self.email = email
        self.day_start = day_start  # earliest time owner is available
        self.day_end = day_end      # latest time owner is available
        self._pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Register a pet under this owner."""
        pass  # TODO: implement

    def remove_pet(self, pet_name: str) -> None:
        """Remove a pet by name."""
        pass  # TODO: implement

    def get_pets(self) -> list[Pet]:
        """Return all pets owned by this owner."""
        pass  # TODO: implement


# ---------------------------------------------------------------------------
# Scheduler
# ---------------------------------------------------------------------------

class Scheduler:
    """Builds a prioritised daily care schedule for all of an owner's pets."""

    def __init__(self, owner: Owner) -> None:
        self.owner = owner

    def prioritize_tasks(self, tasks: list[Task]) -> list[Task]:
        """
        Sort tasks by priority (high → medium → low) and whether they are
        required. Returns a new ordered list.
        """
        pass  # TODO: implement

    def build_schedule(self) -> list[ScheduledTask]:
        """
        Allocate time slots for tasks within the owner's available window.
        Returns a list of ScheduledTask objects in chronological order.
        """
        pass  # TODO: implement

    def explain_plan(self, schedule: list[ScheduledTask]) -> str:
        """
        Return a human-readable explanation of the generated schedule,
        describing why each task was chosen and when it occurs.
        """
        pass  # TODO: implement
