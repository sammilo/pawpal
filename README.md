# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet(s).

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

---

## UML Diagram

```mermaid
classDiagram
    class Owner {
        -String name
        -List~String~ availability
        -Dict preferences
        -List~Pet~ pets
        +get_name() String
        +set_name(name) void
        +get_availability() List
        +set_availability(availability) void
        +get_preferences() Dict
        +set_preferences(preferences) void
        +add_pet(pet) void
        +remove_pet(pet) void
    }

    class Pet {
        -String name
        -String species
        -List feedings
        -List medicines
        -Dict grooming_needs
        -Dict enrichment_needs
        -List~Task~ tasks
        +get_name() String
        +set_name(name) void
        +get_feedings() List
        +set_feedings(feedings) void
        +get_medicines() List
        +set_medicines(medicines) void
        +get_grooming() Dict
        +set_grooming(grooming) void
        +get_enrichment() Dict
        +set_enrichment(enrichment) void
        +get_tasks() List
        +add_task(task) void
        +remove_task(task) void
    }

    class Task {
        -Pet pet
        -String description
        -String priority
        -String due_time
        -int duration
        -bool is_complete
        +mark_complete() void
        +get_pet() Pet
        +set_pet(pet) void
        +get_description() String
        +set_description(desc) void
        +get_priority() String
        +set_priority(priority) void
        +get_due_time() String
        +set_due_time(due_time) void
        +get_duration() int
        +set_duration(duration) void
        +get_is_complete() bool
    }

    class Scheduler {
        -Owner owner
        +order_by_priority(tasks) List~Task~
        +order_by_due_date(tasks) List~Task~
        +recommend_daily_tasks(pets) List~Task~
    }

    Owner "1" *-- "0..*" Pet : owns
    Pet "1" *-- "0..*" Task : has
    Task "0..*" --> "1" Pet : assigned to
    Scheduler "1" --> "1" Owner : uses
    Scheduler ..> Pet : accesses
    Scheduler ..> Task : generates
```
## Testing PawPal+

Run the command python -m pytest to run all 8 tests outlined in tests/text_pawpal.py

Test #1: Selecting complete checkbox marks tasks as completed 
Test #2: Adding a task to a pet increases that pet's task count
Test #3 (3 tests): Completed tasks are excluded from daily schedule
Test #4 (3 tests): Task are sorted in the given order: priority → due_time → owner preference