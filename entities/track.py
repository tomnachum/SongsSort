from typing import Optional
from pydantic import BaseModel
from entities.album import AlbumEntity

class Score(BaseModel):
    album_type: float
    release_year: float
    popularity: float
    total: float

class TrackEntity(BaseModel):
    album: Optional[AlbumEntity]
    name: str
    popularity: Optional[int]
    track_number: int
    score: Optional[Score] = None
    disc_number: int
