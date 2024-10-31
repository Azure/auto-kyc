from pydantic import BaseModel
from typing import Literal


class AddressComparisonResult(BaseModel):
    address1: str
    address2: str
    result: Literal['Same', 'Different']

    def to_string(self) -> str:
        return str(self.dict())    