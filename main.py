from pawpal_system import Owner, Pet, Task, Scheduler


def print_schedule(scheduler, pets):
    """Print today's schedule for the owner."""
    recommended_tasks = scheduler.recommend_daily_tasks(pets)
    
    print("\n" + "="*50)
    print("TODAY'S SCHEDULE")
    print("="*50)
    
    if not recommended_tasks:
        print("No tasks scheduled for today.")
    else:
        # Sort by due_time for display
        sorted_tasks = sorted(recommended_tasks, key=lambda t: t.due_time)
        
        for task in sorted_tasks:
            time_str = f"{task.due_time:02d}:00"
            priority_map = {1: "HIGH", 2: "MEDIUM", 3: "LOW"}
            priority_str = priority_map.get(task.priority, "UNKNOWN")
            
            print(f"\n[{time_str}] {task.description}")
            print(f"  Pet: {task.pet.name}")
            print(f"  Priority: {priority_str}")
            print(f"  Duration: {task.duration} minutes")
    
    print("\n" + "="*50 + "\n")


# Create an owner with availability
owner = Owner(
    name="Sarah",
    availability=[8, 10, 12, 14, 16, 18, 20],  # Available at 8 AM, 10 AM, 12 PM, 2 PM, 4 PM, 6 PM, 8 PM
    preferences={"preferred_times": [8, 10, 12], "task_types": ["feeding", "grooming", "play"]}
)

# Create two pets
dog = Pet(
    name="Max",
    species="dog",
    feedings=[8, 18],
    grooming_needs={"brush": True, "bath": False, "nail_trim": True},
    enrichment_needs={"walk": True, "play": True}
)

cat = Pet(
    name="Whiskers",
    species="cat",
    feedings=[8, 12, 20],
    grooming_needs={"brush": True, "bath": False},
    enrichment_needs={"play": True}
)

# Add pets to owner
owner.add_pet(dog)
owner.add_pet(cat)

# Create tasks with different times
task1 = Task(
    pet=dog,
    description="Feed Max breakfast",
    priority=1,  # HIGH
    due_time=8,
    duration=15
)

task2 = Task(
    pet=dog,
    description="Walk Max in the park",
    priority=1,  # HIGH
    due_time=10,
    duration=45
)

task3 = Task(
    pet=cat,
    description="Feed Whiskers lunch",
    priority=2,  # MEDIUM
    due_time=12,
    duration=10
)

task4 = Task(
    pet=dog,
    description="Brush Max's coat",
    priority=2,  # MEDIUM
    due_time=14,
    duration=30
)

task5 = Task(
    pet=cat,
    description="Play with Whiskers",
    priority=2,  # MEDIUM
    due_time=16,
    duration=20
)

task6 = Task(
    pet=dog,
    description="Feed Max dinner",
    priority=1,  # HIGH
    due_time=18,
    duration=15
)

# Add tasks to pets
dog.add_task(task1)
dog.add_task(task2)
dog.add_task(task4)
dog.add_task(task6)

cat.add_task(task3)
cat.add_task(task5)

# Create scheduler and print the schedule
scheduler = Scheduler(owner)
print_schedule(scheduler, [dog, cat])

# Also print owner and pet details for context
print(f"Owner: {owner.name}")
print(f"Pets: {', '.join([p.name for p in owner.pets])}")
print(f"Owner's availability: {owner.availability} (24-hour format)")
