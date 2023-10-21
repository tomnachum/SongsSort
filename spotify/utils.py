import unicodedata
from unidecode import unidecode

from config.configurations import should_print_changed_album_name_msg, is_test
from spotify.constants import ALBUM_TYPE_ALBUM, ALBUM_TYPE_SINGLE, ALBUM_TYPE_COMPILATION
from spotify.exceptions import SpotifyComparatorException


def remove_apostrophe(input_string):
    return input_string.replace("'", "")


def remove_special_chars(input_string):
    return unicodedata.normalize('NFKD', input_string).encode('ASCII', 'ignore').decode('utf-8')


def parse_str_for_request(input_string):
    return remove_special_chars(remove_apostrophe(input_string))


def extract_params_from_track(track):
    try:
        album_type = track["album"]["album_type"]
        release_year = int(track['album']['release_date'].split('-')[0])
        popularity = track["popularity"]
        if album_type not in [ALBUM_TYPE_ALBUM, ALBUM_TYPE_SINGLE, ALBUM_TYPE_COMPILATION]:
            raise SpotifyComparatorException("Album type is not supported")
        if not 1900 <= release_year < 2030:
            raise SpotifyComparatorException("Release year is not supported")
        if not 0 <= popularity <= 100:
            raise SpotifyComparatorException("Popularity is not supported")
        return album_type, release_year, popularity
    except:
        raise SpotifyComparatorException()


# the best track gets the highest score
def spotify_tracks_comparator(track):
    album_type, release_year, popularity = extract_params_from_track(track)

    # first sore by album type:
    # [1, 3] / -1
    # [0, 2] / :2
    # range [0, 1]
    type_score_dict = {"album": 3, "single": 2, "compilation": 1}
    compare_by_album_type = (type_score_dict[album_type] - 1) / 2

    # then sort by release year
    # (1900, 2100) / -1900
    # (0, 200) / :200
    # range (0, 1)
    compare_by_release_year = 1 - ((release_year - 1900) / 200)

    # then sort by popularity
    # [0, 100] / :100
    # range (0, 1)
    compare_by_album_popularity = popularity / 100

    return 10000 * compare_by_album_type + compare_by_release_year + compare_by_album_popularity


def remove_parentheses(logger, elem):
    if '(' in elem:
        album_name_no_parentheses = elem.split(' (')[0]
        if should_print_changed_album_name_msg:
            logger.info('Changed album name', original_album_name=elem, changed_album_name=album_name_no_parentheses)
        return album_name_no_parentheses
    return elem


def original_escape_string(original_string):
    composed_string = unicodedata.normalize('NFC', original_string)
    escaped_string = composed_string.encode('unicode-escape').decode()
    return original_string.encode('utf-8').decode('unicode-escape')


# if this function returns False, the track will remove
def filter_tracks(logger, track, expected_track_name='', expected_track_artist=''):
    try:
        album = track['album']
        album['images'][0]["url"]
        if any((word.lower() in ['live', 'concert']) for word in track['name'].split()) and \
                all(('live' not in word.lower()) for word in expected_track_name.split()):
            if is_test: logger.error('Live or Concert in track name')
            return False
        if all([(unidecode(expected_track_artist) not in unidecode(artist['name'])
                 and unidecode(artist['name']) not in unidecode(expected_track_artist))
                for artist in album['artists']]):
            if is_test: logger.error('artist not in artists list of album')
            return False
        if album['album_type'] == 'album' and album['total_tracks'] > 30:  # Probably compilation album
            if is_test: logger.error('album has more than 30 songs')
            return False
        return True
    except:
        return False
