# PawPal+ — Final Class Diagram (Mermaid.js)

Paste the block below into https://mermaid.live to render the diagram,
then export as uml_final.png.

```mermaid
classDiagram
    class Task {
        +str title
        +int duration_minutes
        +str priority
        +str time_of_day
        +bool is_required
        +bool completed
        +str frequency
        +date due_date
        +mark_complete() Task or None
    }

    class ScheduledTask {
        +Task task
        +str pet_name
        +str start_time
        +str end_time
        +str reason
    }

    class Pet {
        +str name
        +str species
        +int age
        +str breed
        +list special_needs
        +add_task(task: Task) None
        +get_tasks() list~Task~
    }

    class Owner {
        +str name
        +str email
        +str day_start
        +str day_end
        +add_pet(pet: Pet) None
        +remove_pet(pet_name: str) None
        +get_pets() list~Pet~
    }

    class Scheduler {
        +Owner owner
        +prioritize_tasks(tasks: list) list
        +build_schedule() list~ScheduledTask~
        +sort_by_time(schedule: list) list~ScheduledTask~
        +filter_tasks(pet_name, completed) list
        +complete_task(pet, task) Task or None
        +detect_conflicts(schedule: list) list~str~
        +explain_plan(schedule: list) str
    }

    Owner "1" --> "0..*" Pet : owns
    Pet "1" --> "0..*" Task : has
    Scheduler "1" --> "1" Owner : plans for
    Scheduler "1" --> "0..*" ScheduledTask : produces
    ScheduledTask "1" --> "1" Task : wraps
    Task ..> Task : mark_complete returns next occurrence
```

## Changes from initial UML

| What changed | Why |
|---|---|
| `Task` gained `completed`, `frequency`, `due_date` | Needed for mark-complete, recurring logic, and filtering |
| `Task.mark_complete()` now returns `Optional[Task]` | Recurring tasks need to produce a successor; one-off tasks return `None` |
| `ScheduledTask` gained `pet_name` | Multi-pet schedules need to show which pet each task belongs to |
| `Scheduler` gained `sort_by_time`, `filter_tasks`, `complete_task`, `detect_conflicts` | Phase 4 algorithmic layer |
| `Scheduler._make_reason()` added (private) | Extracted from `build_schedule` to keep that method readable |
