import json
import traceback

import requests
import base64
from config.configurations import is_test, should_print_no_studio_album_msg
from spotify.constants import *
from spotify.exceptions import SpotifyException
from spotify.utils import remove_apostrophe, spotify_tracks_comparator, remove_parentheses, filter_tracks


def get_album_from_spotify(logger, artist_name, track_name):
    token = get_spotify_token()
    response = requests.get(SPOTIFY_API_URL, headers={'Authorization': f'Bearer {token}'}, params={
        'q': f'artist:{remove_apostrophe(artist_name)} track:{remove_apostrophe(track_name)}', 'type': 'track'})
    if response.status_code != 200:
        logger.error('Error occurred while fetching data from Spotify API', artist_name=artist_name,
                     track_name=track_name, status_code=response.status_code, response=response.text,
                     headers=response.headers)
        raise SpotifyException()

    data = response.json()
    if is_test: logger.test("Spotify response: ", response=json.dumps(data))
    if data['tracks']['total'] <= 0:
        logger.error('No albums found', artist_name=artist_name, track_name=track_name)
        raise SpotifyException()

    tracks = data['tracks']['items']
    filtered_tracks = filter(lambda track: filter_tracks(track, track_name), tracks)
    sorted_tracks = sorted(filtered_tracks, key=spotify_tracks_comparator, reverse=True)
    if is_test:
        for track in sorted_tracks:
            del track["album"]["available_markets"], track["album"]["artists"], track["album"]["external_urls"], \
                track["available_markets"], track["artists"], track["disc_number"], track["external_ids"], \
                track["external_urls"], track["id"], track["uri"]
        logger.test("Found items: ", items=json.dumps(sorted_tracks), total=len(sorted_tracks))

    album = sorted_tracks[0]['album']
    if album['album_type'] != 'album' and should_print_no_studio_album_msg:
        logger.info('Could not find studio album', artist_name=artist_name, track_name=track_name,
                    found_album_type=album["album_type"])

    return remove_parentheses(logger, album['name']), album['images'][0]['url']


def get_spotify_token():
    client_creds = f"{CLIENT_ID}:{CLIENT_SECRET}"
    encoded_client_creds = base64.b64encode(client_creds.encode())
    response = requests.post(SPOTIFY_TOKEN_URL, headers={'Authorization': f'Basic {encoded_client_creds.decode()}'},
                             data={'grant_type': 'client_credentials'})
    if response.status_code == 200:
        token_data = response.json()
        return token_data['access_token']
    else:
        raise SpotifyException('Could not get access token for spotify API.')
