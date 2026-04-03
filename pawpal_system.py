from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class Pet:
    name: str
    food_requirements: str
    meds: List[str] = field(default_factory=list)
    grooming_needs: str = ""
    enrichment_done: bool = False

    def get_food_requirements(self) -> str:
        return self.food_requirements

    def get_meds(self) -> List[str]:
        return list(self.meds)

    def get_grooming_needs(self) -> str:
        return self.grooming_needs

    def has_enrichment(self) -> bool:
        return self.enrichment_done

    def set_enrichment_done(self, done: bool) -> None:
        self.enrichment_done = done


@dataclass
class Task:
    description: str
    priority: int
    time_required: int
    pet: Pet

    def get_priority(self) -> int:
        return self.priority

    def set_priority(self, p: int) -> None:
        self.priority = p

    def get_time_required(self) -> int:
        return self.time_required

    def set_time_required(self, minutes: int) -> None:
        self.time_required = minutes


class Owner:
    def __init__(self, name: str, preferences: Dict[str, str] = None, availability: List[str] = None):
        self.name = name
        self.preferences = preferences or {}
        self.availability = availability or []
        self.pets: List[Pet] = []

    def get_preferences(self) -> Dict[str, str]:
        return dict(self.preferences)

    def set_preferences(self, prefs: Dict[str, str]) -> None:
        self.preferences = dict(prefs)

    def get_availability(self) -> List[str]:
        return list(self.availability)

    def set_availability(self, avail: List[str]) -> None:
        self.availability = list(avail)

    def add_pet(self, pet: Pet) -> None:
        if pet not in self.pets:
            self.pets.append(pet)

    def remove_pet(self, pet: Pet) -> None:
        if pet in self.pets:
            self.pets.remove(pet)


class Scheduler:
    def __init__(self, owner: Owner):
        self.owner = owner
        self.tasks: List[Task] = []

    def add_task(self, task: Task) -> None:
        self.tasks.append(task)

    def generate_daily_plan(self) -> List[Task]:
        # TODO: implement scheduling logic using priority + availability + enrichment
        return []

    def explain_plan(self, plan: List[Task]) -> str:
        # TODO: return a human-readable explanation of the decision process
        return ""
