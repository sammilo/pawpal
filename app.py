import json
import os
from datetime import datetime, timedelta, date
import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler, due_before_availability

st.set_page_config(page_title="PawPal+", page_icon="🍄", layout="wide")

st.markdown(
    """
    <style>
    /* ── Global background & text ─────────────────────────────────────── */
    .stApp {
        background-color: #1C2945;
    }

    /* ── Main content area ────────────────────────────────────────────── */
    section[data-testid="stMain"] > div {
        background-color: #1C2945;
    }

    </style>
    """,
    unsafe_allow_html=True,
)

# ── Constants ──────────────────────────────────────────────────────────────────
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pawpal_data.json")

PRIORITY_OPTIONS = ["High - MUST be completed today", "Medium - SHOULD be completed today", "Low - COULD be completed today"]
PRIORITY_TO_INT  = {"High - MUST be completed today": 1, "Medium - SHOULD be completed today": 2, "Low - COULD be completed today": 3}
INT_TO_PRIORITY  = {1: "High - MUST be completed today", 2: "Medium - SHOULD be completed today", 3: "Low - COULD be completed today"}
PRIORITY_LABEL   = {1: "🔴 High", 2: "🟡 Medium", 3: "🟢 Low"}
TASK_TYPE_OPTIONS     = ["Feeding", "Grooming/Hygiene", "Medication", "Enrichment", "Training"]
TASK_CATEGORY_OPTIONS = TASK_TYPE_OPTIONS + ["other"]
RECURRING_OPTIONS     = ["None", "Daily", "Weekly", "Monthly"]
RECURRING_BADGE       = {"Daily": " 🔄 Daily", "Weekly": " 🔄 Weekly", "Monthly": " 🔄 Monthly"}
RECURRING_DELTA       = {"Daily": timedelta(days=1), "Weekly": timedelta(weeks=1), "Monthly": timedelta(days=30)}

# ── Helpers ────────────────────────────────────────────────────────────────────
def fmt_hour(minutes: int) -> str:
    """Convert minutes-from-midnight to a 12-hour display string (e.g. 480 → '8:00 AM', 510 → '8:30 AM')."""
    h, m = divmod(minutes, 60)
    h12 = h % 12 or 12
    suffix = "AM" if h < 12 else "PM"
    return f"{h12}:{m:02d} {suffix}"

def fmt_scheduled_time(minutes: int) -> str:
    """Convert minutes-from-midnight to 12-hour HH:MM (e.g. 490 → '8:10 AM')."""
    h, m = divmod(minutes, 60)
    h12 = h % 12 or 12
    suffix = "AM" if h < 12 else "PM"
    return f"{h12}:{m:02d} {suffix}"

def migrate_availability(availability: list) -> list:
    """Convert old 30-min block format to a 1440-minute array if needed."""
    if isinstance(availability, list) and len(availability) == 1440:
        return availability  # already new format
    arr = [0] * 1440
    for block in availability:
        for minute in range(int(block), min(int(block) + 30, 1440)):
            arr[minute] = 1
    return arr

def availability_to_blocks(availability: list) -> list:
    """Convert a 1440-minute array back to a list of 30-min block start times for the multiselect."""
    if not isinstance(availability, list) or len(availability) != 1440:
        return []
    return [b for b in range(0, 1440, 30) if any(availability[b + i] != 0 for i in range(30))]

def fmt_availability(availability: list) -> str:
    """Convert a 1440-minute array to a human-readable ranges string (e.g. '8:00 AM–10:00 AM')."""
    if not isinstance(availability, list) or len(availability) != 1440:
        return "—"
    ranges = []
    start = None
    for i in range(1441):
        is_avail = i < 1440 and availability[i] != 0
        if is_avail and start is None:
            start = i
        elif not is_avail and start is not None:
            ranges.append(f"{fmt_hour(start)}–{fmt_hour(i)}")
            start = None
    return ", ".join(ranges) or "—"

def release_task_reserved_indices(task_dict: dict) -> None:
    """Switch a task's reserved time slots from 2 back to 1 in the owner's availability array."""
    reserved = task_dict.get("reserved_indices", [])
    if not reserved:
        return
    pet_name = task_dict.get("pet", "")
    owner_name = next(
        (p["owner_name"] for p in st.session_state.pets if p["name"] == pet_name), None
    )
    if owner_name is None:
        return
    owner_idx = next(
        (i for i, o in enumerate(st.session_state.owners) if o["name"] == owner_name), None
    )
    if owner_idx is None:
        return
    avail = st.session_state.owners[owner_idx].get("availability", [])
    if isinstance(avail, list) and len(avail) == 1440:
        for idx in reserved:
            if 0 <= idx < 1440 and avail[idx] == 2:
                avail[idx] = 1
    task_dict["reserved_indices"] = []

def load_data() -> dict:
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE) as f:
                data = json.load(f)
            # Migrate owners with old availability format (list of block starts → 1440-array)
            for owner in data.get("owners", []):
                owner["availability"] = migrate_availability(owner.get("availability", []))
            return data
        except (json.JSONDecodeError, IOError):
            pass
    return {"owners": [], "pets": [], "tasks": []}

def save_data() -> None:
    with open(DATA_FILE, "w") as f:
        json.dump(
            {"owners": st.session_state.owners,
             "pets":   st.session_state.pets,
             "tasks":  st.session_state.tasks},
            f, indent=2,
        )

# ── Session-state bootstrap (runs once per browser session) ───────────────────
if "initialized" not in st.session_state:
    d = load_data()
    st.session_state.owners           = d.get("owners", [])
    st.session_state.pets             = d.get("pets",   [])
    st.session_state.tasks            = d.get("tasks",  [])
    st.session_state.editing_task_idx  = None
    st.session_state.editing_owner_idx = None
    st.session_state.editing_pet_idx   = None
    # Owner-form widget defaults
    st.session_state.form_owner_name  = ""
    st.session_state.form_owner_avail = []
    st.session_state.form_owner_prefs = []
    # Pet-form widget defaults
    st.session_state.form_pet_owner     = ""
    st.session_state.form_pet_name      = ""
    st.session_state.form_pet_species   = "Dog"
    st.session_state.form_pet_meds      = ""
    st.session_state.form_pet_grooming  = False
    st.session_state.form_pet_enrichment = False
    # Task-form widget defaults
    st.session_state.form_task_pet      = ""
    st.session_state.form_task_title    = ""
    st.session_state.form_task_time     = 480
    st.session_state.form_task_duration = 30
    st.session_state.form_task_priority  = PRIORITY_OPTIONS[0]
    st.session_state.form_task_category  = TASK_CATEGORY_OPTIONS[0]
    st.session_state.form_task_recurring = RECURRING_OPTIONS[0]
    st.session_state.task_sort             = "Due Time"
    st.session_state.task_filter_complete  = "All"
    st.session_state.task_filter_pets      = []
    st.session_state.initialized = True

# ── Page header ───────────────────────────────────────────────────────────────
st.title("🍄 PawPal+")
st.markdown(
    """
Welcome to **PawPal+**, your pet care planning assistant.
This app helps you schedule and prioritize care tasks for your pet(s) based on your availability and preferences.
"""
)
st.divider()

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1 – OWNER SETUP
# ══════════════════════════════════════════════════════════════════════════════
st.subheader("👤 Owner Setup")
st.caption("Add owners or use ✏️ to edit an existing one.")

# Consume owner_edit_pending: pre-populate widget keys BEFORE widgets render
if "owner_edit_pending" in st.session_state:
    ep = st.session_state.owner_edit_pending
    del st.session_state["owner_edit_pending"]
    st.session_state.form_owner_name  = ep["name"]
    st.session_state.form_owner_avail = availability_to_blocks(ep["availability"])
    st.session_state.form_owner_prefs = ep["preferences"].get("task_types", [])

# Consume reset_owner_form: clear widget keys BEFORE widgets render
if st.session_state.get("reset_owner_form"):
    del st.session_state["reset_owner_form"]
    st.session_state.form_owner_name  = ""
    st.session_state.form_owner_avail = []
    st.session_state.form_owner_prefs = []

editing_owner = st.session_state.editing_owner_idx is not None

if st.session_state.get("owner_msg"):
    kind, msg = st.session_state.owner_msg
    st.session_state.owner_msg = None
    getattr(st, kind)(msg)

if editing_owner:
    current_owner_name = st.session_state.owners[st.session_state.editing_owner_idx]["name"]
    st.info(f"✏️ Editing **{current_owner_name}** — update fields and click *Update Owner*.")

with st.container(border=True):
    c1, c2 = st.columns(2)
    with c1:
        st.text_input("Owner Name", placeholder="e.g. Jason", key="form_owner_name")
    with c2:
        st.multiselect(
            "Available Hours",
            options=list(range(0, 1440, 30)),
            format_func=fmt_hour,
            key="form_owner_avail",
        )
    st.multiselect(
        "Preferred Activity Types",
        options=TASK_TYPE_OPTIONS,
        help="The scheduler prioritizes tasks matching these types within each time slot.",
        key="form_owner_prefs",
    )
    if not editing_owner:
        owner_submitted = st.button("➕ Add Owner", use_container_width=True)
        owner_cancel = False
    else:
        oc1, oc2 = st.columns(2)
        with oc1:
            owner_submitted = st.button("💾 Update Owner", use_container_width=True)
        with oc2:
            owner_cancel = st.button("✖ Cancel", use_container_width=True, key="cancel_owner")

if owner_submitted:
    name = st.session_state.form_owner_name.strip()
    if not name:
        st.error("Owner name cannot be empty.")
    else:
        clash_idx = next((i for i, o in enumerate(st.session_state.owners) if o["name"] == name), None)
        if clash_idx is not None and clash_idx != st.session_state.editing_owner_idx:
            st.error(f"An owner named '{name}' already exists.")
        else:
            new_avail = [0] * 1440
            for b in st.session_state.form_owner_avail:
                for m in range(b, min(b + 30, 1440)):
                    new_avail[m] = 1
            entry = {
                "name":         name,
                "availability": new_avail,
                "preferences":  {"task_types": st.session_state.form_owner_prefs},
            }
            if editing_owner:
                idx = st.session_state.editing_owner_idx
                old_name = st.session_state.owners[idx]["name"]
                if old_name != name:
                    for p in st.session_state.pets:
                        if p["owner_name"] == old_name:
                            p["owner_name"] = name
                st.session_state.owners[idx] = entry
                st.session_state.owner_msg = ("success", f"✅ Updated owner '{name}'.")
            else:
                st.session_state.owners.append(entry)
                st.session_state.owner_msg = ("success", f"✅ Added owner '{name}'.")
            save_data()
            st.session_state.editing_owner_idx = None
            st.session_state.reset_owner_form  = True
            st.rerun()

if owner_cancel:
    st.session_state.editing_owner_idx = None
    st.session_state.reset_owner_form  = True
    st.rerun()

if st.session_state.owners:
    st.write("**Saved owners:**")
    for i, owner in enumerate(st.session_state.owners):
        with st.container(border=True):
            c1, c2, c3 = st.columns([5, 1, 1])
            with c1:
                avail_str = fmt_availability(owner["availability"])
                prefs_str = ", ".join(owner["preferences"].get("task_types", [])) or "—"
                st.markdown(
                    f"**{owner['name']}**  |  Availability: {avail_str}  |  Preferred: {prefs_str}"
                )
            with c2:
                if st.button("✏️", key=f"edit_owner_{i}", help="Edit owner"):
                    st.session_state.owner_edit_pending  = dict(st.session_state.owners[i])
                    st.session_state.editing_owner_idx   = i
                    st.rerun()
            with c3:
                if st.button("🗑️", key=f"del_owner_{i}", help="Delete owner and all their pets/tasks"):
                    if st.session_state.editing_owner_idx == i:
                        st.session_state.editing_owner_idx = None
                    gone = st.session_state.owners.pop(i)["name"]
                    st.session_state.pets  = [p for p in st.session_state.pets  if p["owner_name"] != gone]
                    alive = {p["name"] for p in st.session_state.pets}
                    st.session_state.tasks = [t for t in st.session_state.tasks if t["pet"] in alive]
                    save_data()
                    st.rerun()

st.divider()

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2 – PET SETUP
# ══════════════════════════════════════════════════════════════════════════════
st.subheader("🐾 Pet Setup")
st.caption("Add pets or use ✏️ to edit an existing one.")

owner_names = [o["name"] for o in st.session_state.owners]

# Keep form_pet_owner valid if the owner list changed since last render
if st.session_state.get("form_pet_owner") not in owner_names:
    st.session_state.form_pet_owner = owner_names[0] if owner_names else ""

# Consume pet_edit_pending: pre-populate widget keys BEFORE widgets render
if "pet_edit_pending" in st.session_state:
    ep = st.session_state.pet_edit_pending
    del st.session_state["pet_edit_pending"]
    st.session_state.form_pet_owner      = ep["owner_name"]
    st.session_state.form_pet_name       = ep["name"]
    st.session_state.form_pet_species    = ep["species"]
    st.session_state.form_pet_meds       = ", ".join(ep.get("medicines", {}).keys())
    st.session_state.form_pet_grooming   = ep.get("grooming_needs", {}).get("completed_today", False)
    st.session_state.form_pet_enrichment = ep.get("enrichment_needs", {}).get("completed_today", False)

# Consume reset_pet_form: clear widget keys BEFORE widgets render
if st.session_state.get("reset_pet_form"):
    del st.session_state["reset_pet_form"]
    st.session_state.form_pet_name       = ""
    st.session_state.form_pet_species    = "Dog"
    st.session_state.form_pet_meds       = ""
    st.session_state.form_pet_grooming   = False
    st.session_state.form_pet_enrichment = False

editing_pet = st.session_state.editing_pet_idx is not None

if st.session_state.get("pet_msg"):
    kind, msg = st.session_state.pet_msg
    st.session_state.pet_msg = None
    getattr(st, kind)(msg)

if not owner_names:
    st.info("Add an owner first before adding pets.")
else:
    if editing_pet:
        current_pet_name = st.session_state.pets[st.session_state.editing_pet_idx]["name"]
        st.info(f"✏️ Editing **{current_pet_name}** — update fields and click *Update Pet*.")

    with st.container(border=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            st.selectbox("Owner", options=owner_names, key="form_pet_owner")
        with c2:
            st.text_input("Pet Name", placeholder="e.g. Max", key="form_pet_name")
        with c3:
            st.selectbox("Species", ["Dog", "Cat", "Other"], key="form_pet_species")

        st.text_input(
            "Medications (optional)",
            placeholder="Comma-separated names, e.g. Revolution, Gabapentin",
            key="form_pet_meds",
        )
        c4, c5 = st.columns(2)
        with c4:
            st.checkbox("Grooming Completed Today", key="form_pet_grooming")
        with c5:
            st.checkbox("Enrichment Completed Today", key="form_pet_enrichment")

        if not editing_pet:
            pet_submitted = st.button("➕ Add Pet", use_container_width=True)
            pet_cancel = False
        else:
            pc1, pc2 = st.columns(2)
            with pc1:
                pet_submitted = st.button("💾 Update Pet", use_container_width=True)
            with pc2:
                pet_cancel = st.button("✖ Cancel", use_container_width=True, key="cancel_pet")

    if pet_submitted:
        name = st.session_state.form_pet_name.strip()
        pet_owner = st.session_state.form_pet_owner
        if not name:
            st.error("Pet name cannot be empty.")
        else:
            clash_idx = next(
                (i for i, p in enumerate(st.session_state.pets)
                 if p["name"] == name and p["owner_name"] == pet_owner),
                None,
            )
            if clash_idx is not None and clash_idx != st.session_state.editing_pet_idx:
                st.error(f"A pet named '{name}' already exists for {pet_owner}.")
            else:
                meds = {m.strip(): "" for m in st.session_state.form_pet_meds.split(",") if m.strip()}
                entry = {
                    "name":             name,
                    "species":          st.session_state.form_pet_species,
                    "owner_name":       pet_owner,
                    "medicines":        meds,
                    "grooming_needs":   {"completed_today": st.session_state.form_pet_grooming},
                    "enrichment_needs": {"completed_today": st.session_state.form_pet_enrichment},
                }
                if editing_pet:
                    idx = st.session_state.editing_pet_idx
                    old_name = st.session_state.pets[idx]["name"]
                    if old_name != name:
                        for t in st.session_state.tasks:
                            if t["pet"] == old_name:
                                t["pet"] = name
                    st.session_state.pets[idx] = entry
                    st.session_state.pet_msg = ("success", f"✅ Updated pet '{name}'.")
                else:
                    st.session_state.pets.append(entry)
                    st.session_state.pet_msg = ("success", f"✅ Added pet '{name}' for {pet_owner}.")
                save_data()
                st.session_state.editing_pet_idx = None
                st.session_state.reset_pet_form  = True
                st.rerun()

    if pet_cancel:
        st.session_state.editing_pet_idx = None
        st.session_state.reset_pet_form  = True
        st.rerun()

if st.session_state.pets:
    st.write("**Saved pets:**")
    for i, pet in enumerate(st.session_state.pets):
        with st.container(border=True):
            c1, c2, c3 = st.columns([5, 1, 1])
            with c1:
                meds_str = ", ".join(pet["medicines"]) or "None"
                groom    = "✅" if pet["grooming_needs"].get("completed_today")   else "❌"
                enrich   = "✅" if pet["enrichment_needs"].get("completed_today") else "❌"
                st.markdown(
                    f"**{pet['name']}** ({pet['species']}) — Owner: {pet['owner_name']}  |  "
                    f"Meds: {meds_str}  |  Grooming: {groom}  |  Enrichment: {enrich}"
                )
            with c2:
                if st.button("✏️", key=f"edit_pet_{i}", help="Edit pet"):
                    st.session_state.pet_edit_pending = dict(st.session_state.pets[i])
                    st.session_state.editing_pet_idx  = i
                    st.rerun()
            with c3:
                if st.button("🗑️", key=f"del_pet_{i}", help="Delete pet and all their tasks"):
                    if st.session_state.editing_pet_idx == i:
                        st.session_state.editing_pet_idx = None
                    gone = st.session_state.pets.pop(i)["name"]
                    st.session_state.tasks = [t for t in st.session_state.tasks if t["pet"] != gone]
                    save_data()
                    st.rerun()

st.divider()

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 3 – TASK MANAGEMENT
# ══════════════════════════════════════════════════════════════════════════════
st.subheader("📋 Tasks")
st.caption("Add tasks for your pets. Each task is tied to a specific pet.")

pet_names = [p["name"] for p in st.session_state.pets]

# Keep form_task_pet valid if the pet list changed since last render
if st.session_state.get("form_task_pet") not in pet_names:
    st.session_state.form_task_pet = pet_names[0] if pet_names else ""

# ── Pre-populate form when an edit was just requested (edit_pending is set in
#    the task list below, then consumed here on the NEXT rerun so that all
#    session-state keys are updated BEFORE the widgets render) ──────────────
# Consume edit_pending: pre-populate widget keys BEFORE widgets render (safe pattern)
if "edit_pending" in st.session_state:
    ep = st.session_state.edit_pending
    del st.session_state["edit_pending"]
    st.session_state.form_task_pet      = ep["pet"]
    st.session_state.form_task_title    = ep["title"]
    st.session_state.form_task_time     = ep["due_time"]
    st.session_state.form_task_duration = ep["duration"]
    st.session_state.form_task_priority  = INT_TO_PRIORITY[ep["priority"]]
    st.session_state.form_task_category  = ep.get("category", TASK_CATEGORY_OPTIONS[0])
    st.session_state.form_task_recurring = ep.get("recurring", RECURRING_OPTIONS[0])

# Consume reset_task_form: clear widget keys BEFORE widgets render (avoids post-render error)
if st.session_state.get("reset_task_form"):
    del st.session_state["reset_task_form"]
    st.session_state.form_task_title    = ""
    st.session_state.form_task_time     = 480
    st.session_state.form_task_duration = 20
    st.session_state.form_task_priority  = PRIORITY_OPTIONS[0]
    st.session_state.form_task_category  = TASK_CATEGORY_OPTIONS[0]
    st.session_state.form_task_recurring = RECURRING_OPTIONS[0]

editing = st.session_state.editing_task_idx is not None

# Show any one-shot feedback messages (set before st.rerun() calls below)
if st.session_state.get("task_msg"):
    kind, msg = st.session_state.task_msg
    st.session_state.task_msg = None
    getattr(st, kind)(msg)

if not pet_names:
    st.info("Add a pet first before adding tasks.")
else:
    if editing:
        current_title = st.session_state.tasks[st.session_state.editing_task_idx]["title"]
        st.info(f"✏️ Editing **{current_title}** — update fields and click *Update Task*.")

    # ── Task form ─────────────────────────────────────────────────────────────
    with st.container(border=True):
        r1c1, r1c2, r1c3, r1c4 = st.columns(4)
        with r1c1:
            st.selectbox("Pet", options=pet_names, key="form_task_pet")
        with r1c2:
            st.text_input("Task Title", placeholder="e.g. Morning walk", key="form_task_title")
        with r1c3:
            st.selectbox("Category", options=TASK_CATEGORY_OPTIONS, key="form_task_category")
        with r1c4:
            st.selectbox("Recurring (Optional)", options=RECURRING_OPTIONS, key="form_task_recurring")

        r2c1, r2c2, r2c3 = st.columns(3)
        with r2c1:
            st.selectbox(
                "Due Time",
                options=list(range(0, 1440, 30)),
                format_func=fmt_hour,
                key="form_task_time",
            )
        with r2c2:
            st.number_input(
                "Duration (min)", min_value=1, max_value=300, step=1, key="form_task_duration"
            )
        with r2c3:
            st.selectbox("Priority", options=PRIORITY_OPTIONS, key="form_task_priority")

        if not editing:
            add_or_update = st.button("➕ Add Task", use_container_width=True)
            cancel = False
        else:
            col1, col2 = st.columns(2)
            with col1:
                add_or_update = st.button("💾 Update Task", use_container_width=True)
            with col2:
                cancel = st.button("✖ Cancel", use_container_width=True)

    if add_or_update:
        title = st.session_state.form_task_title.strip()
        due_time = st.session_state.form_task_time
        pet_name = st.session_state.form_task_pet
        owner_avail = next(
            (o["availability"] for p in st.session_state.pets if p["name"] == pet_name
             for o in st.session_state.owners if o["name"] == p["owner_name"]),
            [],
        )
        if not title:
            st.error("Task title cannot be empty.")
        elif due_before_availability(due_time, owner_avail):
            st.toast(
                f"Due time ({fmt_hour(due_time)}) is earlier than the owner's first "
                f"available hour ({fmt_hour(min(owner_avail))}). "
                "Please adjust the due time or edit the owner's availability.",
                icon="⚠️",
            )
        else:
            task_data = {
                "title":     title,
                "pet":       st.session_state.form_task_pet,
                "category":  st.session_state.form_task_category,
                "duration":  int(st.session_state.form_task_duration),
                "priority":  PRIORITY_TO_INT[st.session_state.form_task_priority],
                "due_time":  st.session_state.form_task_time,
                "recurring": st.session_state.form_task_recurring,
            }
            if editing:
                existing = st.session_state.tasks[st.session_state.editing_task_idx]
                task_data["due_date"] = existing.get("due_date", str(date.today()))
                st.session_state.tasks[st.session_state.editing_task_idx] = task_data
                st.session_state.task_msg = ("success", f"✅ Updated '{title}'.")
            else:
                task_data["due_date"] = str(date.today())
                st.session_state.tasks.append(task_data)
                st.session_state.task_msg = ("success", f"✅ Added '{title}'.")
            save_data()
            st.session_state.editing_task_idx = None
            st.session_state.reset_task_form  = True
            st.rerun()

    if cancel:
        st.session_state.editing_task_idx = None
        st.session_state.reset_task_form  = True
        st.rerun()

    # ── Sort & filter controls ────────────────────────────────────────────────
    sc1, sc2, sc3 = st.columns(3)
    with sc1:
        st.radio(
            "Sort by",
            options=["Due Time", "Priority"],
            horizontal=True,
            key="task_sort",
        )
    with sc2:
        st.selectbox(
            "Filter by Completion",
            options=["All", "Incomplete", "Complete"],
            key="task_filter_complete",
        )
    with sc3:
        st.multiselect(
            "Filter by Pet",
            options=pet_names,
            key="task_filter_pets",
            placeholder="All pets",
        )

    # ── Task list (single flat table) ─────────────────────────────────────────
    if st.session_state.tasks:
        # Build a list of (flat_idx, task) applying the current filter
        visible: list = []
        for flat_idx, task in enumerate(st.session_state.tasks):
            comp = task.get("is_complete", False)
            if st.session_state.task_filter_complete == "Complete"   and not comp: continue
            if st.session_state.task_filter_complete == "Incomplete" and comp:     continue
            if st.session_state.task_filter_pets and task["pet"] not in st.session_state.task_filter_pets:
                continue
            visible.append((flat_idx, task))

        # Apply sort
        if st.session_state.task_sort == "Priority":
            visible.sort(key=lambda x: (x[1]["priority"], x[1]["due_time"]))
        else:  # Due Time
            visible.sort(key=lambda x: (x[1]["due_time"], x[1]["priority"]))

        if not visible:
            st.info("No tasks match the current filter.")
        else:
            # Column layout: #, Pet, Description, Due Time, Duration, Category, Priority, Complete, Edit, Delete
            COL_W = [1, 2, 3, 2, 2, 2, 2, 2, 1, 1]
            HEADERS = ["#", "Pet", "Description", "Due Time", "Duration", "Category", "Priority", "Complete", "", ""]
            hc = st.columns(COL_W)
            for label, col in zip(HEADERS, hc):
                col.markdown(f"**{label}**")

            for row_num, (flat_idx, task) in enumerate(visible, 1):
                rc = st.columns(COL_W)
                rc[0].write(str(row_num))
                rc[1].write(task["pet"])
                rc[2].write(task["title"])
                rc[3].write(fmt_hour(task["due_time"]))
                rc[4].write(f"{task['duration']} min")
                _recurring = task.get("recurring", "None")
                rc[5].write(f"{task.get('category', '—')}{RECURRING_BADGE.get(_recurring, '')}")
                rc[6].write(PRIORITY_LABEL[task["priority"]])

                is_done = task.get("is_complete", False)
                checked = rc[7].checkbox(
                    "Complete",
                    value=is_done,
                    key=f"complete_{flat_idx}",
                    label_visibility="collapsed",
                )
                if checked != is_done:
                    st.session_state.tasks[flat_idx]["is_complete"] = checked
                    if checked:
                        # Release reserved time slots back to available
                        release_task_reserved_indices(st.session_state.tasks[flat_idx])
                        recurring = task.get("recurring", "None")
                        if recurring and recurring != "None":
                            today = date.today()
                            due_date_str = task.get("due_date", str(today))
                            try:
                                due_dt = datetime.strptime(due_date_str, "%Y-%m-%d").date()
                            except (ValueError, TypeError):
                                due_dt = today
                            next_date = due_dt + RECURRING_DELTA[recurring]
                            new_task = dict(task)
                            new_task["is_complete"] = False
                            new_task["due_date"] = str(next_date)
                            new_task["reserved_indices"] = []
                            new_task["scheduled_time"] = -1
                            st.session_state.tasks.append(new_task)
                    save_data()
                    st.rerun()

                if rc[8].button("✏️", key=f"edit_{flat_idx}", help="Edit Task"):
                    st.session_state.edit_pending     = dict(st.session_state.tasks[flat_idx])
                    st.session_state.editing_task_idx = flat_idx
                    st.rerun()

                if rc[9].button("🗑️", key=f"del_{flat_idx}", help="Delete Task"):
                    if st.session_state.editing_task_idx == flat_idx:
                        st.session_state.editing_task_idx = None
                    release_task_reserved_indices(st.session_state.tasks[flat_idx])
                    st.session_state.tasks.pop(flat_idx)
                    save_data()
                    st.rerun()

        if st.button("🗑️ Clear All Tasks"):
            for td in st.session_state.tasks:
                release_task_reserved_indices(td)
            st.session_state.tasks            = []
            st.session_state.editing_task_idx = None
            save_data()
            st.rerun()
    else:
        st.info("No tasks yet. Add one above to get started.")

st.divider()

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 4 – GENERATE SCHEDULE
# ══════════════════════════════════════════════════════════════════════════════
st.subheader("📅 Generate Schedule")
st.caption("Generate an optimized daily schedule for the selected owner.")

if not owner_names:
    st.info("Add an owner, pet, and task first to generate a schedule.")
elif not st.session_state.tasks:
    st.info("Add tasks first to generate a schedule.")
else:
    sel_owner = st.selectbox("Owner to Schedule For:", options=owner_names, key="schedule_owner")

    if st.button("🚀 Generate Daily Schedule", use_container_width=True):
        owner_data = next((o for o in st.session_state.owners if o["name"] == sel_owner), None)
        if owner_data is None:
            st.error("Owner not found.")
        elif not any(v != 0 for v in migrate_availability(owner_data.get("availability", []))):
            st.error("❌ This owner has no availability hours selected.")
        else:
            owner_pets_data = [p for p in st.session_state.pets if p["owner_name"] == sel_owner]
            if not owner_pets_data:
                st.error(f"❌ No pets found for {sel_owner}. Add a pet first.")
            else:
                pet_name_set = {p["name"] for p in owner_pets_data}

                # Ensure availability is in 1440-minute array format (migrate if session has old format)
                owner_data["availability"] = migrate_availability(owner_data.get("availability", []))

                # Reset any previously reserved slots for this owner's tasks (2 → 1)
                avail = owner_data["availability"]
                for i in range(1440):
                    if avail[i] == 2:
                        avail[i] = 1
                for td in st.session_state.tasks:
                    if td["pet"] in pet_name_set:
                        td["reserved_indices"] = []
                        td["scheduled_time"] = -1

                # Build Owner object (shares the same list reference so mutations persist)
                owner_obj = Owner(
                    name=owner_data["name"],
                    availability=avail,
                    preferences=owner_data["preferences"],
                )

                # Build Pet objects
                pet_objects: dict = {}
                for pd in owner_pets_data:
                    p_obj = Pet(
                        name=pd["name"],
                        species=pd["species"],
                        medicines=pd.get("medicines", {}),
                        grooming_needs=pd.get("grooming_needs", {}),
                        enrichment_needs=pd.get("enrichment_needs", {}),
                    )
                    owner_obj.add_pet(p_obj)
                    pet_objects[pd["name"]] = p_obj

                # Attach tasks to their pets; track mapping back to session-state indices
                task_ss_indices: dict = {}  # id(Task object) → session_state.tasks index
                tasks_added = 0
                for ss_idx, td in enumerate(st.session_state.tasks):
                    if td["pet"] in pet_objects:
                        t_obj = Task(
                            pet=pet_objects[td["pet"]],
                            description=td["title"],
                            category=td.get("category", ""),
                            priority=td["priority"],
                            due_time=td["due_time"],
                            duration=td["duration"],
                            is_complete=td.get("is_complete", False),
                        )
                        pet_objects[td["pet"]].add_task(t_obj)
                        task_ss_indices[id(t_obj)] = ss_idx
                        tasks_added += 1

                if tasks_added == 0:
                    st.warning(f"⚠️ None of the saved tasks are assigned to {sel_owner}'s pets.")
                else:
                    # Total available minutes before scheduling
                    total_avail = sum(1 for v in avail if v != 0)

                    pet_list = list(pet_objects.values())
                    scheduler = Scheduler(owner_obj)
                    overload = scheduler.high_priority_overload(pet_list)
                    if overload:
                        high_min, avail_min = overload
                        st.toast(
                            f"High-priority tasks total {high_min} min but you only have "
                            f"{avail_min} min available today. Edit your availability or "
                            "lower some task priorities.",
                            icon="⚠️",
                        )
                    scheduled, unscheduled = scheduler.recommend_daily_tasks(pet_list)

                    # Persist reserved indices and scheduled times back to session state
                    for task in scheduled:
                        ss_idx = task_ss_indices.get(id(task))
                        if ss_idx is not None:
                            st.session_state.tasks[ss_idx]["scheduled_time"] = task.scheduled_time
                            st.session_state.tasks[ss_idx]["reserved_indices"] = task.reserved_indices
                    save_data()

                    st.success(f"✅ Schedule generated for **{sel_owner}**!")

                    total_dur = sum(t.duration for t in scheduled)
                    m1, m2, m3 = st.columns(3)
                    m1.metric("Tasks Scheduled", len(scheduled))
                    m2.metric("Total Time",      f"{total_dur} min")
                    m3.metric("Available Time",  f"{total_avail} min")

                    if scheduled:
                        st.markdown("### 📆 Your Daily Schedule")
                        COL_W_S = [1, 2, 3, 2, 2, 2, 2]
                        HEADERS_S = ["#", "Pet", "Description", "Scheduled Time", "Duration", "Category", "Priority"]
                        hc = st.columns(COL_W_S)
                        for label, col in zip(HEADERS_S, hc):
                            col.markdown(f"**{label}**")
                        for i, task in enumerate(scheduled, 1):
                            rc = st.columns(COL_W_S)
                            rc[0].write(str(i))
                            rc[1].write(task.pet.name)
                            rc[2].write(task.description)
                            rc[3].write(fmt_scheduled_time(task.scheduled_time))
                            rc[4].write(f"{task.duration} min")
                            rc[5].write(task.category or "—")
                            rc[6].write(PRIORITY_LABEL[task.priority])
                    else:
                        st.warning("⚠️ No tasks could be scheduled within the owner's available time before their due times.")

                    if unscheduled:
                        st.markdown("### ⚠️ Unassigned Tasks")
                        st.caption("These tasks could not be fit into any available block before their due time.")
                        COL_W_U = [1, 2, 3, 2, 2, 2, 2]
                        HEADERS_U = ["#", "Pet", "Description", "Due Time", "Duration", "Category", "Priority"]
                        hc2 = st.columns(COL_W_U)
                        for label, col in zip(HEADERS_U, hc2):
                            col.markdown(f"**{label}**")
                        for i, task in enumerate(unscheduled, 1):
                            rc = st.columns(COL_W_U)
                            rc[0].write(str(i))
                            rc[1].write(task.pet.name)
                            rc[2].write(task.description)
                            rc[3].write(fmt_hour(task.due_time))
                            rc[4].write(f"{task.duration} min")
                            rc[5].write(task.category or "—")
                            rc[6].write(PRIORITY_LABEL[task.priority])