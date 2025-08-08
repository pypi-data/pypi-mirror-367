from pydantic import BaseModel
import json
import re
from typing import Literal, Self

from adaptive_harmony import StringThread


class InputConfig(BaseModel):

    @classmethod
    def load_from_file(cls, json_file) -> Self:
        with open(json_file, "r") as f:
            data = json.load(f)
        return cls.model_validate(data)


# Helper classes for inputs
class AdaptiveDataset(BaseModel):
    file: str


class AdaptiveModel(BaseModel):
    path: str

    def __repr__(self) -> str:

        # Redact api_key in the path if present, show only last 3 chars
        def redact_api_key(match):
            key = match.group(2)
            if len(key) > 3:
                redacted = "<REDACTED>" + key[-3:]
            else:
                redacted = "<REDACTED>"
            return f"{match.group(1)}{redacted}"

        redacted_path = re.sub(r"(api_key=)([^&]+)", redact_api_key, self.path)
        return f"AdaptiveModel(path='{redacted_path}')"


class Grade(BaseModel):
    value: float
    grader_name: str
    reason: str | None = None


class EvalSample(BaseModel):
    source: str
    thread: StringThread
    grades: list[Grade]

    class Config:
        arbitrary_types_allowed = True
