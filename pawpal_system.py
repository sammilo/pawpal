from dataclasses import dataclass, field


@dataclass
class Owner:
    name: str
    availability: list = field(default_factory=lambda: [0] * 1440)  # 1440-min array: 0=unavailable, 1=available, 2=reserved
    preferences: dict = field(default_factory=dict)   # e.g. {"task_types": ["feeding", "grooming"]}
    pets: list = field(default_factory=list)

    def add_pet(self, pet):
        """Add a pet to this owner's list and set the pet's owner back-reference."""
        if pet not in self.pets:
            self.pets.append(pet)
            pet.owner = self

    def remove_pet(self, pet):
        """Remove a pet from this owner's list and clear the pet's owner back-reference."""
        if pet in self.pets:
            self.pets.remove(pet)
            pet.owner = None


@dataclass
class Pet:
    name: str
    species: str   # "dog", "cat", "other"
    owner: 'Owner' = None
    feedings: list = field(default_factory=list)
    medicines: dict = field(default_factory=dict)      # e.g. {"Apoquel": "", "Vitamin D": ""}
    grooming_needs: dict = field(default_factory=dict) # e.g. {"completed_today": True}
    enrichment_needs: dict = field(default_factory=dict) # e.g. {"completed_today": False}
    tasks: list = field(default_factory=list)

    def add_task(self, task):
        """Add a task to this pet's list and set the task's pet back-reference."""
        if task not in self.tasks:
            self.tasks.append(task)
            task.pet = self

    def remove_task(self, task):
        """Remove a task from this pet's list and clear the task's pet back-reference."""
        if task in self.tasks:
            self.tasks.remove(task)
            task.pet = None


@dataclass
class Task:
    pet: 'Pet'
    description: str
    priority: int       # 1 (high), 2 (medium), 3 (low)
    due_time: int       # minutes from midnight (e.g. 840 for 2:00 PM)
    duration: int       # duration in minutes
    category: str = ""      # one of TASK_CATEGORY_OPTIONS, e.g. "feeding", "grooming", "other"
    is_complete: bool = False
    recurring: str = ""     # "" = not recurring; "Daily", "Weekly", or "Monthly"
    scheduled_time: int = -1  # actual start in minutes from midnight; -1 = not yet scheduled
    reserved_indices: list = field(default_factory=list)  # indices reserved in owner's availability array

    def mark_complete(self):
        """Mark this task as complete."""
        self.is_complete = True

    def set_pet(self, pet):
        """Reassign this task to a new pet, updating both pets' task lists."""
        if self.pet is not None:
            if self in self.pet.tasks:
                self.pet.tasks.remove(self)
        self.pet = pet
        if pet is not None and self not in pet.tasks:
            pet.tasks.append(self)


def due_before_availability(due_time: int, availability: list) -> bool:
    """Return True if due_time is earlier than the owner's first available minute."""
    if not availability:
        return False
    if len(availability) == 1440:
        # New format: 1440-minute array — find first non-zero (available) minute
        first_avail = next((i for i, v in enumerate(availability) if v != 0), None)
        return first_avail is not None and due_time < first_avail
    else:
        # Legacy format: list of 30-min block start times
        return bool(availability) and due_time < min(availability)


class Scheduler:
    def __init__(self, owner):
        """Initialize the scheduler with an owner whose availability and preferences guide scheduling."""
        self._owner = owner

    def high_priority_overload(self, pets):
        """Return (high_priority_minutes, available_minutes) if the total duration of
        incomplete high-priority tasks exceeds the owner's total availability, else None."""
        high_min = sum(
            task.duration
            for pet in pets
            for task in pet.tasks
            if not task.is_complete and task.priority == 1
        )
        # Count all non-zero minutes as available (1=free, 2=already reserved but still owner time)
        avail_min = sum(1 for v in self._owner.availability if v != 0)
        return (high_min, avail_min) if high_min > avail_min else None

    def order_by_priority(self, tasks):
        """Return tasks sorted from highest to lowest priority (1=high, 2=medium, 3=low)."""
        return sorted(tasks, key=lambda task: task.priority)

    def order_by_due_date(self, tasks):
        """Return tasks sorted by due time, earliest first (minutes from midnight)."""
        return sorted(tasks, key=lambda task: task.due_time)

    def recommend_daily_tasks(self, pets):
        """Schedule tasks into the owner's availability and return (scheduled, unscheduled).

        Sort order: priority (1=high first), then due_time (earliest first), then
        preference (preferred category first).

        Each task is assigned to the first contiguous block of 1s in the availability
        array that fits its full duration and ends at or before its due_time.
        Assigned minutes are switched from 1 → 2 and the task records its reserved_indices.

        Tasks that cannot be fit are returned in the unscheduled list.
        """
        all_tasks = [task for pet in pets for task in pet.tasks if not task.is_complete]

        preferred_types = self._owner.preferences.get("task_types", [])
        all_tasks.sort(key=lambda t: (
            t.priority,
            t.due_time,
            0 if t.category in preferred_types else 1,
        ))

        availability = self._owner.availability  # mutated in-place
        scheduled = []
        unscheduled = []

        for task in all_tasks:
            slot = self._find_slot(availability, task.duration, task.due_time)
            if slot is not None:
                task.scheduled_time = slot
                task.reserved_indices = list(range(slot, slot + task.duration))
                for idx in task.reserved_indices:
                    availability[idx] = 2
                scheduled.append(task)
            else:
                unscheduled.append(task)

        scheduled.sort(key=lambda t: t.scheduled_time)
        return scheduled, unscheduled

    def _find_slot(self, availability, duration, due_time):
        """Find the first start index where `duration` consecutive 1s fit, ending at or before due_time.

        Scans left-to-right tracking runs of 1s. Returns the run_start as soon as
        the run is long enough and run_start + duration <= due_time. If the first
        long-enough run already starts too late (run_start + duration > due_time),
        returns None immediately since all later runs will be even later.
        """
        run_start = None
        for i in range(len(availability)):
            if availability[i] == 1:
                if run_start is None:
                    run_start = i
                run_len = i - run_start + 1
                if run_len >= duration:
                    if run_start + duration <= due_time:
                        return run_start
                    else:
                        # This run starts too late; all future runs will too
                        return None
            else:
                run_start = None
        return None
