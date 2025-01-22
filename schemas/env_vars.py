from pydantic import BaseModel, field_validator
from typing import Optional

class EnvVars(BaseModel):
    SONGS_DIRECTORY: str
    SPOTIFY_CLIENT_ID: str
    SPOTIFY_CLIENT_SECRET: str
    DISCOGS_API_KEY: str
    DISCOGS_API_SECRET: str
    DEBUG: Optional[bool] = False
    _str_to_bool = field_validator("DEBUG", mode='before')(lambda v: v == 'True')

