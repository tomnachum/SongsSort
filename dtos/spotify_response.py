from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, field_validator, ValidationError

class SpotifyAlbumType(str, Enum):  # Inheriting from str makes validation cleaner
    Album = 'album'
    Single = 'single'
    Compilation = 'compilation'

class SimplifiedArtistObject(BaseModel):
    name: Optional[str] = None

class ImageObject(BaseModel):
    url: str

class Album(BaseModel):
    album_type: SpotifyAlbumType
    total_tracks: int
    href: str
    images: List[ImageObject]
    name: str
    release_date: str
    artists: List[SimplifiedArtistObject]

    @field_validator('release_date')
    def validate_release_date(cls, v):
        year = v.split('-')[0]
        if not year.isdigit() or not (1900 <= int(year) < 2030):
            raise ValueError(f'release date not supported release_date={v}')
        return year

class ArtistObject(BaseModel):
    name: Optional[str] = None

class TrackObject(BaseModel):
    album: Optional[Album] = None
    artists: Optional[List[ArtistObject]] = None
    duration_ms: Optional[int] = None
    href: Optional[str] = None
    name: Optional[str] = None
    popularity: Optional[int] = 0
    preview_url: Optional[str] = None
    track_number: Optional[int] = None
    disc_number: Optional[int] = None

    @field_validator('popularity')
    def validate_popularity(cls, v):
        if not 0 <= v <= 100:
            raise ValueError(f'popularity not supported popularity={v}')
        return v

class Tracks(BaseModel):
    href: str
    limit: int
    next: Optional[str] = None
    offset: int
    previous: Optional[str] = None
    total: int
    items: List[TrackObject]

    @field_validator("items", mode="before")
    @classmethod
    def filter_invalid_items(cls, value):
        valid_items = []
        for item in value:
            try:
                valid_items.append(TrackObject(**item))
            except ValidationError as e:
                print(e)
                pass
        return valid_items

class SpotifyResponse(BaseModel):
    tracks: Tracks