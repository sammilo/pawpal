class Owner:
    def __init__(self, name, availability=None, preferences=None):
        self._name = name
        self._availability = availability or []  # list of time slots using 24-hour ints (e.g. [8, 12, 18] for 8 AM, 12 PM, 6 PM)
        self._preferences = preferences or {}    # e.g. {"preferred_time": "10-12", "task_types": ["feeding", "grooming"]}
        self._pets = []

    def get_name(self):
        pass

    def set_name(self, name):
        pass

    def get_availability(self):
        pass

    def set_availability(self, availability):
        pass

    def get_preferences(self):
        pass

    def set_preferences(self, preferences):
        pass

    def add_pet(self, pet):
        # Also sets pet._owner = self to maintain back-reference
        pass

    def remove_pet(self, pet):
        # Also clears pet._owner = None on removal
        pass


class Pet:
    def __init__(self, name, species):
        self._name = name
        self._species = species   # "dog", "cat", "other"
        self._owner = None        # back-reference to the Owner; set via Owner.add_pet()
        self._feedings = []       # list of feeding times (24-hour ints, e.g. [8, 18] for 8 AM and 6 PM)
        self._medicines = {}      # dictionary of medication schedules (e.g. {"antibiotic": "8, 20", "vitamins": "12"})
        self._grooming_needs = {} # e.g. {"brush": True, "bath": False, "nail_trim": True}
        self._enrichment_needs = {} # e.g. {"walk": True, "play": False}
        self._tasks = []          # list of Task objects

    def get_name(self):
        pass

    def set_name(self, name):
        pass

    def get_feedings(self):
        pass

    def set_feedings(self, feedings):
        pass

    def get_medicines(self):
        pass

    def set_medicines(self, medicines):
        pass

    def get_grooming(self):
        pass

    def set_grooming(self, grooming):
        pass

    def get_enrichment(self):
        pass

    def set_enrichment(self, enrichment):
        pass

    def get_owner(self):
        pass

    def set_owner(self, owner):
        pass

    def get_tasks(self):
        pass

    def add_task(self, task):
        # Appends task to self._tasks and sets task._pet = self (bidirectional sync)
        pass

    def remove_task(self, task):
        # Removes task from self._tasks and sets task._pet = None (bidirectional sync)
        pass


class Task:
    def __init__(self, pet, description, priority, due_time, duration):
        self._pet = pet             # Pet object this task is assigned to
        self._description = description
        self._priority = priority   # "high = 1", "medium = 2", "low = 3"
        self._due_time = due_time   # 24-hour int (e.g. 14 for 2 PM)
        self._duration = duration   # duration in minutes (int)
        self._is_complete = False

    def mark_complete(self):
        pass

    def get_pet(self):
        pass

    def set_pet(self, pet):
        # Removes self from old pet's _tasks, sets self._pet = pet,
        # then adds self to new pet's _tasks (bidirectional sync)
        pass

    def get_description(self):
        pass

    def set_description(self, desc):
        pass

    def get_priority(self):
        pass

    def set_priority(self, priority):
        pass

    def get_due_time(self):
        pass

    def set_due_time(self, due_time):
        pass

    def get_duration(self):
        pass

    def set_duration(self, duration):
        pass

    def get_is_complete(self):
        pass


class Scheduler:
    def __init__(self, owner):
        self._owner = owner  # Owner object — provides availability and preferences

    def order_by_priority(self, tasks):
        # Returns a new list of tasks sorted by priority (high → medium → low)
        pass

    def order_by_due_date(self, tasks):
        # Returns a new list of tasks sorted by due_time (earliest first)
        pass

    def recommend_daily_tasks(self, pets):
        # Accepts a list of Pet objects (all pets belonging to self._owner).
        # Collects tasks across all pets, then filters and sorts them based on:
        #   - task priority (1=high, 2=medium, 3=low)
        #   - task due_time (24-hour int, earliest first)
        #   - owner availability (self._owner.get_availability())
        #   - owner preferences (self._owner.get_preferences())
        # Allocates the owner's total available time across all pets before returning
        # the combined recommended task list.
        pass
