import json
import unicodedata
from unidecode import unidecode
from spotify.schemas.spotify_item import TrackObject
from utils.logger import Logger


def remove_apostrophe(input_string):
    return input_string.replace("'", "")


def remove_special_chars(input_string):
    return unicodedata.normalize('NFKD', input_string).encode('ASCII', 'ignore').decode('utf-8')


def parse_str_for_request(input_string):
    return remove_special_chars(remove_apostrophe(input_string))


# the best track gets the highest score
def spotify_tracks_comparator(track: TrackObject):
    # first sore by album type:
    # [1, 3] / -1
    # [0, 2] / :2
    # range [0, 1]
    type_score_dict = {"album": 3, "single": 2, "compilation": 1}
    compare_by_album_type = (type_score_dict[track.album.album_type] - 1) / 2

    # then sort by release year
    # (1900, 2100) / -1900
    # (0, 200) / :200
    # range (0, 1)
    compare_by_release_year = 1 - ((int(track.album.release_date) - 1900) / 200)

    # then sort by popularity
    # [0, 100] / :100
    # range (0, 1)
    compare_by_album_popularity = track.popularity / 100

    return 10000 * compare_by_album_type + compare_by_release_year + compare_by_album_popularity


def remove_parentheses(logger, elem):
    if '(' in elem:
        album_name_no_parentheses = elem.split(' (')[0]
        logger.info('Changed album name', original_album_name=elem, changed_album_name=album_name_no_parentheses)
        return album_name_no_parentheses
    return elem


def original_escape_string(original_string):
    return original_string.encode('utf-8').decode('unicode-escape')


# if this function returns False, the track will remove
def filter_tracks(logger: Logger, track: TrackObject, expected_track_name: str = '', expected_track_artist: str = ''):
    try:
        if not track.album or not track.album.images:
            return False
        if any((word.lower() in ['live', 'concert']) for word in track.name.split()) and \
                all(('live' not in word.lower()) for word in expected_track_name.split()):
            return False
        if all([(unidecode(expected_track_artist) not in unidecode(artist.name)
                 and unidecode(artist.name) not in unidecode(expected_track_artist))
                for artist in track.album.artists]):
            return False
        if track.album.album_type == 'album' and track.album.total_tracks > 30 and track.popularity > 20:  # Probably compilation album
            return False
        return True
    except:
        return False


def tracks_to_json(all_tracks):
    return json.dumps(list(map(lambda track: (track.dict()), all_tracks)))
