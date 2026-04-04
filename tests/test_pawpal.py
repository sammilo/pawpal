import pytest
from pawpal_system import Pet, Task

def test_task_completion_changes_status():
    """Verify that calling mark_complete() changes the task's status."""
    pet = Pet("Buddy", "dog")
    task = Task(pet=pet, description="Take dog for a walk", priority=1, due_time=10, duration=45)
    assert task.is_complete is False
    task.mark_complete()
    assert task.is_complete is True

def test_adding_task_increases_pet_task_count():
    """Verify that adding a task to a Pet increases that pet's task count."""
    pet = Pet("Buddy", "dog")
    initial_count = len(pet.tasks)
    task = Task(pet=pet, description="Give food to pet", priority=1, due_time=8, duration=15)
    pet.add_task(task)
    assert len(pet.tasks) == initial_count + 1