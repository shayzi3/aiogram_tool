import json
from dataclasses import dataclass
from datetime import datetime
from typing import Self


@dataclass
class UserLimit:
    requests: int | float
    time: datetime

    def __post_init__(self) -> None:
        if isinstance(self.time, str):
            self.time = datetime.fromisoformat(self.time)

    def json(self) -> str:
        return json.dumps({"requests": self.requests, "time": self.time.isoformat()})

    @classmethod
    def from_json(cls, obj: str) -> Self:
        data = json.loads(obj)
        if not all(key in data for key in cls.__dataclass_fields__.keys()):
            raise ValueError("Invalid json for UserLimit")
        return cls(**data)
