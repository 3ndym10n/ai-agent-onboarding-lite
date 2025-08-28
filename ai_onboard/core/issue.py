from dataclasses import dataclass
from typing import Optional, Literal

Severity = Literal["error","warn","info"]

@dataclass
class Issue:
    rule_id: str
    severity: Severity
    message: str
    file: Optional[str] = None
    line: Optional[int] = None
    confidence: float = 0.0
    remediation: Optional[str] = None
