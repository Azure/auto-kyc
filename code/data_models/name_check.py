from pydantic import BaseModel
from typing import Literal


class NameComparisonResult(BaseModel):
    name1: str
    name2: str
    result: Literal['Same', 'Different', 'ToBeChecked']

    def to_string(self) -> str:
        return str(self.dict())