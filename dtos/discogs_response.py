from typing import List
from pydantic import BaseModel


class DiscogsResults(BaseModel):
    type: str
    format: List[str]
    title: str


class DiscogsResponse(BaseModel):
    results: List[DiscogsResults]
