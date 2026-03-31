"""
Demo script — run with: python main.py
Verifies that the PawPal+ scheduling logic works end-to-end.
"""

from pawpal_system import Owner, Pet, Task, Scheduler


def main():
    # --- Owner ---------------------------------------------------------------
    owner = Owner(name="Jordan", email="jordan@example.com",
                  day_start="08:00", day_end="20:00")

    # --- Pets ----------------------------------------------------------------
    mochi = Pet(name="Mochi", species="dog", age=3, breed="Shiba Inu")
    luna  = Pet(name="Luna",  species="cat", age=5)

    # --- Tasks for Mochi -----------------------------------------------------
    mochi.add_task(Task(title="Morning walk",   duration_minutes=30, priority="high",   time_of_day="morning"))
    mochi.add_task(Task(title="Feed breakfast", duration_minutes=10, priority="high"))
    mochi.add_task(Task(title="Playtime",       duration_minutes=20, priority="medium", is_required=False))

    # --- Tasks for Luna ------------------------------------------------------
    luna.add_task(Task(title="Feed breakfast",  duration_minutes=5,  priority="high"))
    luna.add_task(Task(title="Clean litter box",duration_minutes=10, priority="medium"))
    luna.add_task(Task(title="Brushing",        duration_minutes=15, priority="low",    is_required=False))

    # --- Register pets -------------------------------------------------------
    owner.add_pet(mochi)
    owner.add_pet(luna)

    # --- Build and display schedule ------------------------------------------
    scheduler = Scheduler(owner)
    schedule  = scheduler.build_schedule()
    print(scheduler.explain_plan(schedule))


if __name__ == "__main__":
    main()
