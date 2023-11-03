from typing import List
from pydantic import BaseModel
from entities.artist import ArtistEntity
from entities.image import ImageEntity


class AlbumEntity(BaseModel):
    images: List[ImageEntity]
    artists: List[ArtistEntity]
    album_type: str
    total_tracks: int
    name: str
    release_date: str
