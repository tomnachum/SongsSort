from pydantic import BaseModel


class ImageEntity(BaseModel):
    url: str
