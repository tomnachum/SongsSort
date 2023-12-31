from pydantic import BaseModel, field_validator


class EnvVars(BaseModel):
    IS_TEST: bool = False
    _str_to_bool = field_validator("IS_TEST", mode='before')(lambda v: v == 'True')
    TEST_FOLDER_PATH: str
    INVALID_FOLDER_PATH: str
    MODIFIED_FOLDER_PATH: str
    FOLDER_PATH: str
    SPOTIFY_CLIENT_ID: str
    SPOTIFY_CLIENT_SECRET: str
    DISCOGS_API_KEY: str
    DISCOGS_API_SECRET: str
