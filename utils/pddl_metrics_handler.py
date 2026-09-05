import json
from dataclasses import dataclass, asdict
from utils import utils
from utils.json_serializable import JsonSerializable
from utils.lore_document import LoreDocument

@dataclass
class PddlMetric(JsonSerializable):
    lore_document: LoreDocument
    syntax_errors: int
    logic_errors: int
    critical_errors: int

    def total_errors(self):
        return self.syntax_errors + self.logic_errors + self.critical_errors

    def __init__(self, lore_document: LoreDocument, syntax_errors: int = 0, logic_errors: int = 0, critical_errors: int = 0):
        self.lore_document = lore_document
        self.syntax_errors = syntax_errors
        self.logic_errors = logic_errors
        self.critical_errors = critical_errors

    def __str__(self) -> str:
        return self.to_json()

PDDL_METRICS: dict[str, list[PddlMetric]] = {}

def get_pddl_metrics(file_path: str) -> list[PddlMetric]:
    global PDDL_METRICS
    if file_path not in PDDL_METRICS:
        PDDL_METRICS[file_path] = load_metrics(file_path)
    return PDDL_METRICS[file_path]

def load_metrics(file_path: str) -> list[PddlMetric]:
    json_data = json.loads(utils.load(file_path))
    metrics = []
    for obj in json_data:
        metrics.append(PddlMetric.from_dict(obj))
    return metrics

def save_metrics(file_path: str, metrics: list[PddlMetric]) -> None:
    json_data = json.dumps(metrics, default=asdict, indent=4)
    utils.store(file_path, json_data)