from dataclasses import dataclass, asdict
from enum import Enum

class ValidationRes(Enum):
    VALID = [0, 1, 2, 3]
    SYNTAX_ERROR = [31]
    NO_SOLUTION = [10, 11, 12]
    CRITICAL_ERROR = [20, 21, 22, 23, 24, 30, 32, 33, 34, 35, 36, 37]

@dataclass
class PddlAnalysis:
    exit_code: ValidationRes
    log: str

    def __init__(self, exit_code, log=None):
        self.exit_code = exit_code
        self.log = log

    def __str__(self) -> str:
        return asdict(self).__str__()