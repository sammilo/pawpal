import pytest
from pawpal_system import Owner, Pet, Task, Scheduler

# ── Scenario 1: checking complete marks tasks as completed ──────────────────
def test_task_completion_changes_status():
    """Verify that calling mark_complete() changes the task's status."""
    pet = Pet("Buddy", "dog")
    task = Task(pet=pet, description="Take dog for a walk", priority=1, due_time=10, duration=45)
    assert task.is_complete is False
    task.mark_complete()
    assert task.is_complete is True

# ── Scenario 2: adding a task to a pet increases that pet's task count ──────────────────
def test_adding_task_increases_pet_task_count():
    """Verify that adding a task to a Pet increases that pet's task count."""
    pet = Pet("Buddy", "dog")
    initial_count = len(pet.tasks)
    task = Task(pet=pet, description="Give food to pet", priority=1, due_time=8, duration=15)
    pet.add_task(task)
    assert len(pet.tasks) == initial_count + 1

# ── Scenario 3: completed tasks are excluded from scheduling ──────────────────

def test_completed_task_not_scheduled():
    """A task marked complete must not appear in the scheduled output."""
    owner = make_owner_with_availability(480, 600)  # 8:00–10:00 AM
    pet = make_pet(owner)

    done = Task(pet=pet, description="Already done", priority=1, due_time=600, duration=20, is_complete=True)
    pet.add_task(done)

    scheduled, _ = Scheduler(owner).recommend_daily_tasks([pet])

    scheduled_descs = [t.description for t in scheduled]
    assert "Already done" not in scheduled_descs


def test_only_incomplete_tasks_are_scheduled():
    """When a mix of complete and incomplete tasks exist, only incomplete ones are scheduled."""
    owner = make_owner_with_availability(480, 660)  # 8:00–11:00 AM
    pet = make_pet(owner)

    incomplete = Task(pet=pet, description="Morning walk",  priority=2, due_time=600, duration=30)
    complete   = Task(pet=pet, description="Evening walk",  priority=2, due_time=600, duration=30, is_complete=True)
    pet.add_task(incomplete)
    pet.add_task(complete)

    scheduled, _ = Scheduler(owner).recommend_daily_tasks([pet])

    assert len(scheduled) == 1
    assert scheduled[0].description == "Morning walk"


def test_all_complete_tasks_yields_empty_schedule():
    """If every task is complete, both scheduled and unscheduled lists must be empty."""
    owner = make_owner_with_availability(480, 600)
    pet = make_pet(owner)

    for desc in ("Feed", "Groom", "Walk"):
        t = Task(pet=pet, description=desc, priority=1, due_time=600, duration=15, is_complete=True)
        pet.add_task(t)

    scheduled, unscheduled = Scheduler(owner).recommend_daily_tasks([pet])

    assert scheduled == []
    assert unscheduled == []


# ── Scenario 4: sort order — priority → due_time → owner preference ───────────

def test_sort_by_priority():
    """Higher-priority tasks (lower int) are scheduled before lower-priority ones."""
    owner = make_owner_with_availability(480, 720)  # 8:00 AM–12:00 PM
    pet = make_pet(owner)

    low  = Task(pet=pet, description="Low",    priority=3, due_time=720, duration=10)
    med  = Task(pet=pet, description="Medium", priority=2, due_time=720, duration=10)
    high = Task(pet=pet, description="High",   priority=1, due_time=720, duration=10)
    for t in (low, med, high):
        pet.add_task(t)

    scheduled, _ = Scheduler(owner).recommend_daily_tasks([pet])

    descs = [t.description for t in scheduled]
    assert descs.index("High") < descs.index("Medium") < descs.index("Low")


def test_same_priority_sorted_by_due_time():
    """Among tasks with equal priority, the one with the earlier due_time is scheduled first."""
    owner = make_owner_with_availability(480, 720)
    pet = make_pet(owner)

    later  = Task(pet=pet, description="Later due",  priority=2, due_time=660, duration=10)
    earlier = Task(pet=pet, description="Earlier due", priority=2, due_time=540, duration=10)
    for t in (later, earlier):
        pet.add_task(t)

    scheduled, _ = Scheduler(owner).recommend_daily_tasks([pet])

    descs = [t.description for t in scheduled]
    assert descs.index("Earlier due") < descs.index("Later due")


def test_same_priority_and_due_time_preferred_category_first():
    """Among tasks with equal priority and due_time, the preferred category is scheduled first."""
    owner = make_owner_with_availability(480, 720, preferences={"task_types": ["Feeding"]})
    pet = make_pet(owner)

    non_pref = Task(pet=pet, description="Grooming task", priority=2, due_time=600, duration=10, category="Grooming")
    pref     = Task(pet=pet, description="Feeding task",  priority=2, due_time=600, duration=10, category="Feeding")
    for t in (non_pref, pref):
        pet.add_task(t)

    scheduled, _ = Scheduler(owner).recommend_daily_tasks([pet])

    descs = [t.description for t in scheduled]
    assert descs.index("Feeding task") < descs.index("Grooming task")

# ── Helpers ───────────────────────────────────────────────────────────────────

def make_owner_with_availability(start: int, end: int, preferences: dict = None) -> Owner:
    """Return an Owner with availability[start:end] set to 1."""
    owner = Owner(name="Test Owner", preferences=preferences or {})
    for i in range(start, end):
        owner.availability[i] = 1
    return owner


def make_pet(owner: Owner, name: str = "Buddy") -> Pet:
    pet = Pet(name=name, species="dog")
    owner.add_pet(pet)
    return pet
