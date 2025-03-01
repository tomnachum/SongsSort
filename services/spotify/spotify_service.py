import time
import unicodedata
from typing import List, Optional
import requests
import base64
from dtos.resolvers.dto_resolvers import track_dto_to_entity
from dtos.spotify_response import SpotifyResponse, TrackObject
from http import HTTPStatus
from entities.track import TrackEntity
from services.interfaces.fetch_tracks_info_service import FetchTracksInfoService
from shared.constants import SPOTIFY_API_URL, SPOTIFY_TOKEN_URL
from shared.logger import Logger
from typing import Dict

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
        self.max_retries = 3

    def _get_spotify_token(self):
        client_creds = f"{self._client_id}:{self._client_secret}"
        encoded_client_creds = base64.b64encode(client_creds.encode())
        response = requests.post(SPOTIFY_TOKEN_URL, headers={'Authorization': f'Basic {encoded_client_creds.decode()}'},
                                 data={'grant_type': 'client_credentials'})
        if response.status_code == HTTPStatus.OK:
            token_data = response.json()
            return token_data['access_token']
        else:
            self._logger.error('Could not get access token for spotify_service API.')
            raise ValueError()

    def get_tracks(self, artist: Optional[str] = None, track: Optional[str] = None) -> List[TrackEntity]:
        query = ''
        if artist: query += f'artist:{_parse_str_for_request(artist)}'
        if track: query += f' track:{_parse_str_for_request(track)}'
        params = {'q': query, 'type': 'track'}
        url = SPOTIFY_API_URL
        has_more_tracks = True
        all_tracks: List[TrackObject] = []
        while has_more_tracks:
            spotify_response = self.request_spotify_with_retry(artist, params, track, url)
            all_tracks += spotify_response.tracks.items
            url = spotify_response.tracks.next
            params = None
            has_more_tracks = spotify_response.tracks.next is not None
        if len(all_tracks) <= 0:
            self._logger.error('No albums found', artist=artist, track=track)
            raise ValueError
        return [track_dto_to_entity(t) for t in all_tracks]

    def request_spotify_with_retry(self, artist: str, params: Dict, track: str, url: str) -> SpotifyResponse:
        retries = 0
        while retries <= self.max_retries:
            response = requests.get(url, headers={'Authorization': f'Bearer {self._token}'}, params=params)
            if 'Retry-After' in response.headers:
                wait = int(response.headers['Retry-After'])
                self._logger.warning(f'Spotify reached the rate limit, waiting for {wait} seconds...', )
                time.sleep(wait)
                retries += 1
                continue
            elif response.status_code == HTTPStatus.UNAUTHORIZED:
                self._logger.warning('Token expired for spotify API. generating a new one', artist=artist,
                                     track=track, status_code=response.status_code, res=response.text)
                self._token = self._get_spotify_token()
                retries += 1
                continue
            elif response.status_code != HTTPStatus.OK:
                self._logger.error('Error occurred while fetching data from Spotify API', artist=artist,
                                   track=track, status_code=response.status_code, res=response.text)
                raise ValueError
            return SpotifyResponse(**response.json())
        self._logger.error(f'Spotify API failed {self.max_retries} times, exiting', artist=artist, track=track)
        raise ValueError
