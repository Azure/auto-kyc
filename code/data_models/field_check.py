from pydantic import BaseModel
from typing import Literal

class FieldComparisonResult(BaseModel):
    field1: str
    field2: str
    result: Literal['Same', 'Different', 'ToBeChecked']

    def to_string(self) -> str:
        return str(self.dict())