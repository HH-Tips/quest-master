from dataclasses import dataclass
from utils.json_serializable import JsonSerializable

@dataclass
class LoreDocument(JsonSerializable):
    lore: str
    branching_factor: tuple[int, int]
    depth_constraint: tuple[int, int]

    def __init__(self, lore: str, branching_factor: tuple[int, int], depth_constraint: tuple[int, int]):
        self.lore = lore
        self.branching_factor = branching_factor
        self.depth_constraint = depth_constraint

    def __str__(self):
        return self.to_json()