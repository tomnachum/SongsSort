from pydantic import BaseModel, field_validator


class EnvVars(BaseModel):
    IS_TEST: bool
    _str_to_bool = field_validator("IS_TEST", mode='before')(lambda v: v == 'True')
    FOLDER_PATH: str
    SPOTIFY_CLIENT_ID: str
    SPOTIFY_CLIENT_SECRET: str
    DISCOGS_API_KEY: str
    DISCOGS_API_SECRET: str
