import json
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

    def _get_studio_albums(self, artist: str, track: str) -> List[str]:
        response = requests.get(DISCOGS_URL, params={
            'artist': artist,
            'type': 'master',
            'key': self._api_key,
            'secret': self._api_secret,
            'track': track
        })
        # self._logger.info(json.dumps(json.loads(response.text)))

        if response.status_code != HTTPStatus.OK:
            self._logger.error('Error occurred while fetching data from discogs API', artist_name=artist,
                               status_code=response.status_code, response=json.dumps(response.text),
                               headers=json.dumps(response.headers))
            raise DiscogsException()

        discogs_response = DiscogsResponse(**response.json())
        albums = discogs_response.results
        if len(albums) <= 0:
            return []

        album_names = []
        for album in albums:
            if 'Compilation' not in album.format and 'Single' not in album.format and 'Album' in album.format and 'Live' not in album.title:
                album_name = album.title.split(" - ")[1]
                album_names.append(album_name)
        return album_names

    def verify_albums(self, artist: str, track: str, tracks: List[TrackEntity]):
        studio_albums = self._get_studio_albums(artist=artist, track=track)
        verified_albums = []
        for t in tracks:
            for w in t.album.name.split(' ('):
                if w in studio_albums and t.album.album_type == 'album':
                    t.album.album_type = "verified_album"
                    verified_albums.append(t.album.name)
        if len(verified_albums) > 0:
            self._logger.test('Found albums using discogs', verified_albums=verified_albums)
