from pydantic import BaseModel


class ArtistEntity(BaseModel):
    name: str
