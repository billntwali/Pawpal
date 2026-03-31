import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="wide")
st.title("🐾 PawPal+")
st.caption("A smart daily care planner for your pets.")

# ---------------------------------------------------------------------------
# Session state — Owner is created once and persisted across reruns
# ---------------------------------------------------------------------------
if "owner" not in st.session_state:
    st.session_state["owner"] = Owner(name="Jordan", day_start="08:00", day_end="20:00")

owner: Owner = st.session_state["owner"]


# ---------------------------------------------------------------------------
# Sidebar: Owner settings
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("Owner Settings")
    new_name  = st.text_input("Your name",         value=owner.name)
    new_start = st.text_input("Day start (HH:MM)",  value=owner.day_start)
    new_end   = st.text_input("Day end   (HH:MM)",  value=owner.day_end)
    if st.button("Save settings"):
        owner.name      = new_name
        owner.day_start = new_start
        owner.day_end   = new_end
        st.session_state.pop("last_schedule", None)   # invalidate cached schedule
        st.success(f"Saved for {owner.name}.")

    st.divider()
    st.caption("PawPal+ v1.0 · Module 2 Project")


# ---------------------------------------------------------------------------
# Main tabs
# ---------------------------------------------------------------------------
tab_pets, tab_schedule, tab_browse = st.tabs(["🐾 Pets & Tasks", "📅 Today's Schedule", "🔍 Browse & Filter"])


# ===========================================================================
# Tab 1 — Pets & Tasks
# ===========================================================================
with tab_pets:

    # ---- Add pet -----------------------------------------------------------
    st.subheader("Your Pets")
    with st.form("add_pet_form", clear_on_submit=True):
        p1, p2, p3 = st.columns(3)
        with p1:
            pet_name = st.text_input("Pet name")
        with p2:
            species  = st.selectbox("Species", ["dog", "cat", "rabbit", "bird", "other"])
        with p3:
            age      = st.number_input("Age (years)", min_value=0, max_value=30, value=1)
        breed = st.text_input("Breed (optional)")
        add_pet_btn = st.form_submit_button("Add Pet")

    if add_pet_btn and pet_name.strip():
        owner.add_pet(Pet(
            name=pet_name.strip(), species=species,
            age=int(age), breed=breed.strip(),
        ))
        st.session_state.pop("last_schedule", None)
        st.success(f"{pet_name.strip()} added!")

    pets = owner.get_pets()
    if pets:
        for pet in pets:
            label = f"**{pet.name}** — {pet.species}, age {pet.age}"
            if pet.breed:
                label += f", {pet.breed}"
            st.markdown(label)
    else:
        st.info("No pets yet. Add one above.")

    st.divider()

    # ---- Add task ----------------------------------------------------------
    st.subheader("Add a Task")
    if not pets:
        st.info("Add a pet first before adding tasks.")
    else:
        with st.form("add_task_form", clear_on_submit=True):
            selected_pet_name = st.selectbox("Assign to pet", [p.name for p in pets])
            t1, t2, t3 = st.columns(3)
            with t1:
                task_title = st.text_input("Task title", value="Morning walk")
            with t2:
                duration   = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
            with t3:
                priority   = st.selectbox("Priority", ["high", "medium", "low"])
            t4, t5, t6 = st.columns(3)
            with t4:
                time_pref  = st.selectbox("Preferred time", ["Any", "morning", "afternoon", "evening"])
            with t5:
                frequency  = st.selectbox("Frequency", ["once", "daily", "weekly"])
            with t6:
                is_required = st.checkbox("Required?", value=True)
            add_task_btn = st.form_submit_button("Add Task")

        if add_task_btn and task_title.strip():
            target = next(p for p in pets if p.name == selected_pet_name)
            target.add_task(Task(
                title=task_title.strip(),
                duration_minutes=int(duration),
                priority=priority,
                time_of_day=None if time_pref == "Any" else time_pref,
                frequency=frequency,
                is_required=is_required,
            ))
            st.session_state.pop("last_schedule", None)
            st.success(f"'{task_title.strip()}' added to {selected_pet_name}.")

        # Show each pet's task list
        for pet in pets:
            tasks = pet.get_tasks()
            if tasks:
                with st.expander(f"{pet.name}'s tasks ({len(tasks)})"):
                    rows = [
                        {
                            "Title": t.title,
                            "Duration (min)": t.duration_minutes,
                            "Priority": t.priority,
                            "Frequency": t.frequency,
                            "Required": "yes" if t.is_required else "no",
                            "Done": "✓" if t.completed else "",
                        }
                        for t in tasks
                    ]
                    st.table(rows)


# ===========================================================================
# Tab 2 — Today's Schedule
# ===========================================================================
with tab_schedule:
    st.subheader("Today's Schedule")
    scheduler = Scheduler(owner)

    if st.button("Generate schedule", type="primary"):
        all_tasks = [t for p in owner.get_pets() for t in p.get_tasks()]
        if not all_tasks:
            st.warning("Add at least one task before generating a schedule.")
        else:
            st.session_state["last_schedule"] = scheduler.build_schedule()

    if "last_schedule" in st.session_state:
        schedule = st.session_state["last_schedule"]

        if not schedule:
            st.info("No tasks to schedule — all may already be completed, or none fit the time window.")
        else:
            # ---- Conflict warnings ----------------------------------------
            conflicts = scheduler.detect_conflicts(schedule)
            if conflicts:
                for w in conflicts:
                    st.warning(w)
            else:
                st.success(f"{len(schedule)} task(s) scheduled between {owner.day_start} and {owner.day_end} — no conflicts detected.")

            # ---- Sort toggle ----------------------------------------------
            sort_order = st.radio(
                "Display order",
                ["Priority order", "Chronological"],
                horizontal=True,
            )
            display = scheduler.sort_by_time(schedule) if sort_order == "Chronological" else schedule

            st.divider()

            # ---- Task cards -----------------------------------------------
            for i, entry in enumerate(display):
                col_info, col_btn = st.columns([6, 1])
                with col_info:
                    freq_badge  = f"  `{entry.task.frequency}`" if entry.task.frequency != "once" else ""
                    status_icon = "✅" if entry.task.completed else "🔲"
                    st.markdown(
                        f"{status_icon} **{entry.start_time} – {entry.end_time}** &nbsp;|&nbsp; "
                        f"**{entry.pet_name}**: {entry.task.title} "
                        f"({entry.task.duration_minutes} min, {entry.task.priority}){freq_badge}"
                    )
                    st.caption(entry.reason)
                with col_btn:
                    if not entry.task.completed:
                        if st.button("Mark done", key=f"done_{i}"):
                            target_pet = next(
                                p for p in owner.get_pets() if p.name == entry.pet_name
                            )
                            next_task = scheduler.complete_task(target_pet, entry.task)
                            st.session_state.pop("last_schedule", None)
                            if next_task:
                                st.success(
                                    f"'{next_task.title}' is recurring — next occurrence queued for {next_task.due_date}."
                                )
                            st.rerun()


# ===========================================================================
# Tab 3 — Browse & Filter
# ===========================================================================
with tab_browse:
    st.subheader("Browse & Filter Tasks")
    scheduler = Scheduler(owner)
    pets      = owner.get_pets()

    if not pets:
        st.info("No pets registered yet. Head to Pets & Tasks to get started.")
    else:
        fa, fb = st.columns(2)
        with fa:
            filter_pet    = st.selectbox("Filter by pet",    ["All"] + [p.name for p in pets])
        with fb:
            filter_status = st.selectbox("Filter by status", ["All", "Pending", "Completed"])

        pet_name_arg  = None if filter_pet    == "All" else filter_pet
        completed_arg = None if filter_status == "All" else (filter_status == "Completed")

        results = scheduler.filter_tasks(pet_name=pet_name_arg, completed=completed_arg)

        if results:
            rows = [
                {
                    "Pet":       pn,
                    "Title":     t.title,
                    "Priority":  t.priority,
                    "Duration":  t.duration_minutes,
                    "Frequency": t.frequency,
                    "Required":  "yes" if t.is_required else "no",
                    "Status":    "✓ Done" if t.completed else "Pending",
                }
                for pn, t in results
            ]
            st.dataframe(rows, use_container_width=True)
            st.caption(f"{len(rows)} task(s) shown.")
        else:
            st.info("No tasks match the selected filters.")
