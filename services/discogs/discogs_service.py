from http import HTTPStatus
from typing import List
import requests
from dtos.discogs_response import DiscogsResponse
from entities.track import TrackEntity
from shared.constants import DISCOGS_URL
from shared.exceptions import DiscogsException
from shared.logger import Logger


class DiscogsService:
    def __init__(self, api_key: str, api_secret: str, logger: Logger):
        self._api_key = api_key
        self._api_secret = api_secret
        self._logger = logger

    def _get_studio_albums(self, artist: str) -> List[str]:
        response = requests.get(DISCOGS_URL, params={
            'q': artist,
            'type': 'master',
            'key': self._api_key,
            'secret': self._api_secret
        })

        if response.status_code != HTTPStatus.OK:
            self._logger.error('Error occurred while fetching data from discogs API', artist_name=artist,
                               status_code=response.status_code, response=response.text,
                               headers=response.headers)
            raise DiscogsException()

        discogs_response = DiscogsResponse(**response.json())
        albums = discogs_response.results
        if len(albums) <= 0:
            return []

        album_names = []
        for album in albums:
            if 'Compilation' not in album.format and 'Single' not in album.format and 'Album' in album.format:
                album_name = album.title.split(" - ")[1]
                album_names.append(album_name)
        return album_names

    def verify_albums(self, artist: str, tracks: List[TrackEntity]):
        studio_albums = self._get_studio_albums(artist=artist)
        for t in tracks:
            if t.album.name in studio_albums and t.album.album_type == 'album':
                t.album.album_type = "verified_album"
