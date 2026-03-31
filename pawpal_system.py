"""
PawPal+ — backend logic layer.
All classes representing the domain model and scheduling live here.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional


PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}


# ---------------------------------------------------------------------------
# Data-only objects (dataclasses)
# ---------------------------------------------------------------------------

@dataclass
class Task:
    """A single pet-care activity that can be scheduled."""
    title: str
    duration_minutes: int
    priority: str                  # "low" | "medium" | "high"
    time_of_day: Optional[str] = None  # "morning" | "afternoon" | "evening" | None
    is_required: bool = True
    completed: bool = False

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.completed = True


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
        self._tasks.append(task)

    def get_tasks(self) -> list[Task]:
        """Return all tasks associated with this pet."""
        return list(self._tasks)


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
        self._pets.append(pet)

    def remove_pet(self, pet_name: str) -> None:
        """Remove a pet by name."""
        self._pets = [p for p in self._pets if p.name != pet_name]

    def get_pets(self) -> list[Pet]:
        """Return all pets owned by this owner."""
        return list(self._pets)


# ---------------------------------------------------------------------------
# Scheduler
# ---------------------------------------------------------------------------

class Scheduler:
    """Builds a prioritised daily care schedule for all of an owner's pets."""

    def __init__(self, owner: Owner) -> None:
        self.owner = owner

    def prioritize_tasks(self, tasks: list[tuple]) -> list[tuple]:
        """Sort (task, pet_name) pairs: required first, then high → medium → low priority."""
        return sorted(
            tasks,
            key=lambda pair: (
                0 if pair[0].is_required else 1,
                PRIORITY_ORDER.get(pair[0].priority, 2),
            ),
        )

    def build_schedule(self) -> list[ScheduledTask]:
        """Fit prioritised tasks into the owner's available time window and return the plan."""
        all_tasks: list[tuple] = []
        for pet in self.owner.get_pets():
            for task in pet.get_tasks():
                all_tasks.append((task, pet.name))

        ordered = self.prioritize_tasks(all_tasks)

        schedule: list[ScheduledTask] = []
        current = datetime.strptime(self.owner.day_start, "%H:%M")
        day_end = datetime.strptime(self.owner.day_end, "%H:%M")

        for task, pet_name in ordered:
            end = current + timedelta(minutes=task.duration_minutes)
            if end > day_end:
                continue  # skip tasks that won't fit; try smaller ones
            schedule.append(ScheduledTask(
                task=task,
                pet_name=pet_name,
                start_time=current.strftime("%H:%M"),
                end_time=end.strftime("%H:%M"),
                reason=self._make_reason(task, pet_name),
            ))
            current = end

        return schedule

    def _make_reason(self, task: Task, pet_name: str) -> str:
        """Build a plain-English reason string for a scheduled task."""
        required_label = "required" if task.is_required else "optional"
        return f"{task.priority.capitalize()}-priority {required_label} task for {pet_name}."

    def explain_plan(self, schedule: list[ScheduledTask]) -> str:
        """Return a human-readable summary of the full schedule."""
        if not schedule:
            return "No tasks could be scheduled within the available time window."

        lines = [f"Today's Schedule for {self.owner.name}'s pets", "=" * 50]
        for st in schedule:
            status = "✓" if st.task.completed else " "
            lines.append(
                f"[{status}] {st.start_time} – {st.end_time}  "
                f"{st.pet_name}: {st.task.title}  "
                f"({st.task.duration_minutes} min)  |  {st.reason}"
            )
        lines.append("=" * 50)
        lines.append(f"Total tasks: {len(schedule)}")
        return "\n".join(lines)
