from enum import Enum
from typing import List
from pydantic import BaseModel, field_validator
from entities.artist import ArtistEntity
from entities.image import ImageEntity


class AlbumType(str, Enum):
    VERIFIED_ALBUM = "verified_album"
    ALBUM = "album"
    SINGLE = "single"
    COMPILATION = "compilation"

    @staticmethod
    def list():
        return list(map(lambda c: c.value, AlbumType))


class AlbumEntity(BaseModel):
    images: List[ImageEntity]
    artists: List[ArtistEntity]
    album_type: str
    total_tracks: int
    name: str
    release_date: str
    track_number: int

    @field_validator('album_type')
    def validate_album_type(cls, v):
        if v not in AlbumType.list():
            raise ValueError(f'album type not supported album_type={v}')
        return v
