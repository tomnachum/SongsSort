import unicodedata
from typing import List
import requests
import base64
from dtos.spotify_response import SpotifyResponse, TrackObject
from http import HTTPStatus
from entities.track import TrackEntity
from services.interfaces.fetch_tracks_info_service import FetchTracksInfoService
from shared.constants import SPOTIFY_API_URL, SPOTIFY_TOKEN_URL
from shared.exceptions import SpotifyException
from shared.logger import Logger


def _parse_str_for_request(input_string):
    str_no_apostrophe = input_string.replace("'", "")
    str_no_special_chars = unicodedata.normalize('NFKD', str_no_apostrophe).encode('ASCII', 'ignore').decode('utf-8')
    return str_no_special_chars


class SpotifyService(FetchTracksInfoService):
    def __init__(self, client_id: str, client_secret: str, logger: Logger):
        self._logger = logger
        self._client_id = client_id
        self._client_secret = client_secret
        self._token = self._get_spotify_token()

    def _get_spotify_token(self):
        client_creds = f"{self._client_id}:{self._client_secret}"
        encoded_client_creds = base64.b64encode(client_creds.encode())
        response = requests.post(SPOTIFY_TOKEN_URL, headers={'Authorization': f'Basic {encoded_client_creds.decode()}'},
                                 data={'grant_type': 'client_credentials'})
        if response.status_code == HTTPStatus.OK:
            token_data = response.json()
            return token_data['access_token']
        else:
            raise SpotifyException('Could not get access token for spotify_service API.')

    def get_tracks(self, artist, track) -> List[TrackEntity]:
        parsed_artist_name = _parse_str_for_request(artist)
        parsed_track_name = _parse_str_for_request(track)
        headers = {'Authorization': f'Bearer {self._token}'}
        params = {'q': f'artist:{parsed_artist_name} track:{parsed_track_name}', 'type': 'track'}
        url = SPOTIFY_API_URL
        has_more_tracks = True
        all_tracks: List[TrackObject] = []
        while has_more_tracks:
            response = requests.get(url, headers=headers, params=params)
            if response.status_code != HTTPStatus.OK:
                self._logger.error('Error occurred while fetching data from Spotify API', artist=artist,
                                   track=track, status_code=response.status_code, response=response.text,
                                   headers=response.headers)
                raise SpotifyException()
            spotify_response = SpotifyResponse(**response.json())
            all_tracks += spotify_response.tracks.items
            url = spotify_response.tracks.next
            params = None
            has_more_tracks = spotify_response.tracks.next is not None
        return [TrackEntity(**t.model_dump()) for t in all_tracks]
