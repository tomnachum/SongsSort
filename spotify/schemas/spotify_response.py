from typing import List, Optional

from pydantic import BaseModel

from spotify.schemas.spotify_item import TrackObject


class Tracks(BaseModel):
    href: str
    limit: int
    next: Optional[str]
    offset: int
    previous: Optional[str]
    total: int
    items: List[TrackObject]


class SpotifyResponse(BaseModel):
    tracks: Tracks
