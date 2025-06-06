from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, field_validator, ValidationError


class SpotifyAlbumType(Enum):
    Album = 'album'
    Single = 'single'
    Compilation = 'compilation'

    @staticmethod
    def list():
        return list(map(lambda c: c.value, SpotifyAlbumType))


class SimplifiedArtistObject(BaseModel):
    name: Optional[str]


class ImageObject(BaseModel):
    url: str


class Album(BaseModel):
    album_type: str
    total_tracks: int
    href: str
    images: List[ImageObject]
    name: str
    release_date: str
    artists: List[SimplifiedArtistObject]

    @field_validator('album_type')
    def validate_album_type(cls, v):
        if v not in SpotifyAlbumType.list():
            raise ValueError(f'album type not supported album_type={v}')
        return v

    @field_validator('release_date')
    def validate_release_date(cls, v):
        v = v.split('-')[0]
        if not 1900 <= int(v) < 2030:
            raise ValueError(f'release date not supported release_date={v}')
        return v


class ArtistObject(BaseModel):
    name: Optional[str]


class TrackObject(BaseModel):
    album: Optional[Album]
    artists: Optional[List[ArtistObject]]
    duration_ms: Optional[int]
    href: Optional[str]
    name: Optional[str]
    popularity: Optional[int]
    preview_url: Optional[str]
    track_number: Optional[int]
    disc_number: Optional[int]

    @field_validator('popularity')
    def validate_popularity(cls, v):
        if not 0 <= v <= 100:
            raise ValueError(f'popularity not supported popularity={v}')
        return v


class Tracks(BaseModel):
    href: str
    limit: int
    next: Optional[str]
    offset: int
    previous: Optional[str]
    total: int
    items: List[TrackObject]

    @field_validator("items", mode="before")
    @classmethod
    def filter_invalid_items(cls, value):
        valid_items = []
        for item in value:
            try:
                valid_items.append(TrackObject(**item))
            except ValidationError:
                pass  # Ignore invalid items
        return valid_items


class SpotifyResponse(BaseModel):
    tracks: Tracks
