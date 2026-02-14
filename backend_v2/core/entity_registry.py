from typing import Dict
from core.models import Entity


class EntityRegistry:
    def __init__(self):
        self.entities: Dict[str, Entity] = {}

    def get_or_create(self, name: str) -> Entity:
        key = name.lower()

        if key not in self.entities:
            self.entities[key] = Entity(name=name)

        return self.entities[key]

    def update_mentions(self, name: str):
        entity = self.get_or_create(name)
        entity.mention_count += 1
        return entity

    def all_entities(self):
        return list(self.entities.values())
