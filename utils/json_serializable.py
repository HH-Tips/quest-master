import json
from dataclasses import dataclass, asdict 

@dataclass
class JsonSerializable:

    def to_json(self) -> str:
        return json.dumps(asdict(self), sort_keys=True, indent=4)

    @classmethod
    def from_json(cls, json_data: str) -> 'JsonSerializable':
        data = json.loads(json_data)
        return cls(**data)

    @classmethod
    def from_dict(cls, data: dict) -> 'JsonSerializable':
        return cls(**data)