from typing import Optional
from pydantic import BaseModel
from entities.album import AlbumEntity


class TrackEntity(BaseModel):
    album: Optional[AlbumEntity]
    name: str
    popularity: Optional[int]
