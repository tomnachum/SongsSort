from typing import Optional
from uuid import uuid4

from pydantic import BaseModel, Field
from entities.album import AlbumEntity

class Score(BaseModel):
    album_type: float
    release_year: float
    popularity: float
    total: float

class TrackEntity(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    album: Optional[AlbumEntity]
    name: str
    popularity: Optional[int]
    track_number: int
    score: Optional[Score] = None
    disc_number: int
