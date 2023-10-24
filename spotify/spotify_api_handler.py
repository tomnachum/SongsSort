import json
import requests
import base64
from config.configurations import is_test, should_print_no_studio_album_msg
from spotify.constants import *
from spotify.exceptions import SpotifyException
from spotify.schemas.spotify_response import SpotifyResponse
from spotify.utils import spotify_tracks_comparator, remove_parentheses, filter_tracks, parse_str_for_request
from http import HTTPStatus

def get_album_from_spotify(logger, artist_name, track_name):
    all_tracks = get_all_tracks_from_spotify(logger, artist_name, track_name)

    if len(all_tracks) <= 0:
        logger.error('No albums found', artist_name=artist_name, track_name=track_name)
        raise SpotifyException()

    filtered_tracks = list(filter(lambda track: filter_tracks(logger, track, track_name, artist_name), all_tracks))
    sorted_tracks = sorted(filtered_tracks, key=spotify_tracks_comparator, reverse=True)
    if is_test: logger.test("Found items: ", response_tracks=all_tracks, response_tracks_len=len(all_tracks),
                            filtered_tracks=filtered_tracks, filtered_tracks_len=len(filtered_tracks),
                            sorted_tracks=sorted_tracks, sorted_tracks_len=len(sorted_tracks))

    if not sorted_tracks:
        logger.error('Sorted Albums is empty', artist_name=artist_name, track_name=track_name)
        raise SpotifyException()

    album = sorted_tracks[0].album
    if album.album_type != 'album' and should_print_no_studio_album_msg:
        logger.info('Could not find studio album', artist_name=artist_name, track_name=track_name,
                    found_album_type=album.album_type)

    return remove_parentheses(logger, album.name), album.images[0].url


def get_all_tracks_from_spotify(logger, artist_name, track_name):
    token = get_spotify_token()
    headers = {'Authorization': f'Bearer {token}'}
    params = {'q': f'artist:{parse_str_for_request(artist_name)} track:{parse_str_for_request(track_name)}', 'type': 'track'}
    url = SPOTIFY_API_URL
    has_more_tracks = True
    all_tracks = []
    while has_more_tracks:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code != HTTPStatus.OK:
            logger.error('Error occurred while fetching data from Spotify API', artist_name=artist_name,
                         track_name=track_name, status_code=response.status_code, response=response.text,
                         headers=response.headers)
            raise SpotifyException()
        spotify_response = SpotifyResponse(**response.json())
        all_tracks += spotify_response.tracks.items
        if is_test: logger.info('Called spotify API', total_tracks=len(all_tracks))
        url = spotify_response.tracks.next
        params = None
        has_more_tracks = spotify_response.tracks.next is not None
    return all_tracks


def get_spotify_token():
    client_creds = f"{CLIENT_ID}:{CLIENT_SECRET}"
    encoded_client_creds = base64.b64encode(client_creds.encode())
    response = requests.post(SPOTIFY_TOKEN_URL, headers={'Authorization': f'Basic {encoded_client_creds.decode()}'},
                             data={'grant_type': 'client_credentials'})
    if response.status_code == HTTPStatus.OK:
        token_data = response.json()
        return token_data['access_token']
    else:
        raise SpotifyException('Could not get access token for spotify API.')
