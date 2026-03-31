import streamlit as st

# Step 1: Import the classes from our logic layer
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

# ---------------------------------------------------------------------------
# Step 2: Manage application "memory" with st.session_state
#
# Streamlit reruns this file from top to bottom on every interaction.
# st.session_state is a persistent dictionary that survives reruns.
# We only create a fresh Owner on the very first load — after that we
# always pull the existing object out of the "vault".
# ---------------------------------------------------------------------------
if "owner" not in st.session_state:
    st.session_state["owner"] = Owner(name="Jordan", day_start="08:00", day_end="20:00")

owner: Owner = st.session_state["owner"]


# ---------------------------------------------------------------------------
# Owner settings
# ---------------------------------------------------------------------------
st.subheader("Owner Settings")
c1, c2, c3 = st.columns(3)
with c1:
    new_name  = st.text_input("Your name",          value=owner.name)
with c2:
    new_start = st.text_input("Day start (HH:MM)",  value=owner.day_start)
with c3:
    new_end   = st.text_input("Day end   (HH:MM)",  value=owner.day_end)

if st.button("Save owner settings"):
    owner.name      = new_name
    owner.day_start = new_start
    owner.day_end   = new_end
    st.success(f"Saved settings for {owner.name}.")

st.divider()


# ---------------------------------------------------------------------------
# Step 3a: "Add Pet" form → wired to owner.add_pet()
# ---------------------------------------------------------------------------
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

# Wire: form submit → owner.add_pet(Pet(...))
if add_pet_btn and pet_name.strip():
    owner.add_pet(Pet(
        name=pet_name.strip(),
        species=species,
        age=int(age),
        breed=breed.strip(),
    ))
    st.success(f"{pet_name.strip()} added to your household!")

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


# ---------------------------------------------------------------------------
# Step 3b: "Add Task" form → wired to pet.add_task()
# ---------------------------------------------------------------------------
st.subheader("Add a Task")

if not pets:
    st.info("Add a pet first before adding tasks.")
else:
    pet_names = [p.name for p in pets]

    with st.form("add_task_form", clear_on_submit=True):
        selected_pet_name = st.selectbox("Assign to pet", pet_names)
        t1, t2, t3 = st.columns(3)
        with t1:
            task_title = st.text_input("Task title", value="Morning walk")
        with t2:
            duration   = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
        with t3:
            priority   = st.selectbox("Priority", ["high", "medium", "low"])
        t4, t5 = st.columns(2)
        with t4:
            time_pref  = st.selectbox("Preferred time", ["Any", "morning", "afternoon", "evening"])
        with t5:
            is_required = st.checkbox("Required?", value=True)
        add_task_btn = st.form_submit_button("Add Task")

    # Wire: form submit → target_pet.add_task(Task(...))
    if add_task_btn and task_title.strip():
        target_pet = next(p for p in pets if p.name == selected_pet_name)
        target_pet.add_task(Task(
            title=task_title.strip(),
            duration_minutes=int(duration),
            priority=priority,
            time_of_day=None if time_pref == "Any" else time_pref,
            is_required=is_required,
        ))
        st.success(f"'{task_title.strip()}' added to {selected_pet_name}.")

    # Show each pet's current task list
    for pet in pets:
        tasks = pet.get_tasks()
        if tasks:
            with st.expander(f"{pet.name}'s tasks ({len(tasks)})"):
                rows = [
                    {
                        "Title": t.title,
                        "Duration (min)": t.duration_minutes,
                        "Priority": t.priority,
                        "Required": "yes" if t.is_required else "no",
                        "Done": "✓" if t.completed else "",
                    }
                    for t in tasks
                ]
                st.table(rows)

st.divider()


# ---------------------------------------------------------------------------
# Step 3c: "Generate Schedule" button → wired to Scheduler.build_schedule()
# ---------------------------------------------------------------------------
st.subheader("Build Schedule")

if st.button("Generate schedule"):
    all_tasks = [t for p in owner.get_pets() for t in p.get_tasks()]
    if not all_tasks:
        st.warning("Add at least one task before generating a schedule.")
    else:
        scheduler = Scheduler(owner)
        schedule  = scheduler.build_schedule()
        plan_text = scheduler.explain_plan(schedule)
        st.code(plan_text, language=None)
        st.success(
            f"{len(schedule)} task(s) scheduled between "
            f"{owner.day_start} and {owner.day_end}."
        )
