from dataclasses import dataclass, field


@dataclass
class Owner:
    name: str
    availability: list = field(default_factory=list)  # list of time slots using 24-hour ints (e.g. [8, 12, 18] for 8 AM, 12 PM, 6 PM)
    preferences: dict = field(default_factory=dict)   # e.g. {"preferred_times": [8, 10, 12], "task_types": ["feeding", "grooming"]}
    pets: list = field(default_factory=list)

    def add_pet(self, pet):
        """Add a pet to this owner's list and set the pet's owner back-reference."""
        # Also sets pet.owner = self to maintain back-reference
        if pet not in self.pets:
            self.pets.append(pet)
            pet.owner = self

    def remove_pet(self, pet):
        """Remove a pet from this owner's list and clear the pet's owner back-reference."""
        # Also clears pet.owner = None on removal
        if pet in self.pets:
            self.pets.remove(pet)
            pet.owner = None


@dataclass
class Pet:
    name: str
    species: str   # "dog", "cat", "other"
    owner: 'Owner' = None        # back-reference to the Owner; set via Owner.add_pet()
    feedings: list = field(default_factory=list)       # list of feeding times (24-hour ints, e.g. [8, 18] for 8 AM and 6 PM)
    medicines: dict = field(default_factory=dict)      # dictionary of medication schedules (e.g. {"antibiotic": "8, 20", "vitamins": "12"})
    grooming_needs: dict = field(default_factory=dict) # e.g. {"brush": True, "bath": False, "nail_trim": True}
    enrichment_needs: dict = field(default_factory=dict) # e.g. {"walk": True, "play": False}
    tasks: list = field(default_factory=list)          # list of Task objects

    def add_task(self, task):
        """Add a task to this pet's list and set the task's pet back-reference."""
        # Appends task to self.tasks and sets task.pet = self (bidirectional sync)
        if task not in self.tasks:
            self.tasks.append(task)
            task.pet = self

    def remove_task(self, task):
        """Remove a task from this pet's list and clear the task's pet back-reference."""
        # Removes task from self.tasks and sets task.pet = None (bidirectional sync)
        if task in self.tasks:
            self.tasks.remove(task)
            task.pet = None


@dataclass
class Task:
    pet: 'Pet'
    description: str
    priority: int       # integer: 1 (high), 2 (medium), 3 (low)
    due_time: int       # 24-hour int (e.g. 14 for 2 PM)
    duration: int       # duration in minutes (int)
    is_complete: bool = False

    def mark_complete(self):
        """Mark this task as complete."""
        self.is_complete = True

    def set_pet(self, pet):
        """Reassign this task to a new pet, updating both pets' task lists."""
        # Removes self from old pet's tasks, sets self.pet = pet,
        # then adds self to new pet's tasks (bidirectional sync)
        if self.pet is not None:
            if self in self.pet.tasks:
                self.pet.tasks.remove(self)
        self.pet = pet
        if pet is not None and self not in pet.tasks:
            pet.tasks.append(self)


class Scheduler:
    def __init__(self, owner):
        """Initialize the scheduler with an owner whose availability and preferences guide scheduling."""
        self._owner = owner  # Owner object — provides availability and preferences

    def order_by_priority(self, tasks):
        """Return tasks sorted from highest to lowest priority (1=high, 2=medium, 3=low)."""
        # Priority: 1 = high, 2 = medium, 3 = low
        return sorted(tasks, key=lambda task: task.priority)

    def order_by_due_date(self, tasks):
        """Return tasks sorted by due time, earliest first (24-hour int)."""
        return sorted(tasks, key=lambda task: task.due_time)

    def recommend_daily_tasks(self, pets):
        """Return a prioritized task list across all pets, filtered to fit the owner's available time."""
        # Accepts a list of Pet objects (all pets belonging to self._owner).
        # Collects tasks across all pets, then filters and sorts them based on:
        #   - task priority (1=high, 2=medium, 3=low)
        #   - task due_time (24-hour int, earliest first)
        #   - owner availability (self._owner.availability)
        #   - owner preferences (self._owner.preferences)
        # Allocates the owner's total available time across all pets before returning
        # the combined recommended task list.
        
        # Collect all tasks from all pets that are not yet complete
        all_tasks = []
        for pet in pets:
            for task in pet.tasks:
                if not task.is_complete:
                    all_tasks.append(task)
        
        # Sort by priority first (high to low), then by due_time (earliest first)
        sorted_tasks = sorted(all_tasks, key=lambda task: (task.priority, task.due_time))
        
        # Calculate total available time (in minutes)
        availability = self._owner.availability
        # Assume each available hour slot is 60 minutes
        total_available_minutes = len(availability) * 60
        
        # Filter tasks that fit within owner's availability and preferences
        recommended_tasks = []
        time_allocated = 0
        
        for task in sorted_tasks:
            # Check if task fits within available time
            task_duration = task.duration
            if time_allocated + task_duration <= total_available_minutes:
                # Check if task's due_time falls within owner's available hours
                task_due_time = task.due_time
                if task_due_time in availability:
                    recommended_tasks.append(task)
                    time_allocated += task_duration
        
        return recommended_tasks