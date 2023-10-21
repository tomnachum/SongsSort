from config.configurations import should_print_changed_album_name_msg
from spotify.constants import ALBUM_TYPE_ALBUM, ALBUM_TYPE_SINGLE, ALBUM_TYPE_COMPILATION
from spotify.exceptions import SpotifyComparatorException


def remove_apostrophe(input_string):
    return input_string.replace("'", "")


def extract_params_from_track(track):
    try:
        album_type = track["album"]["album_type"]
        release_year = int(track['album']['release_date'].split('-')[0])
        popularity = track["popularity"]
        if album_type not in [ALBUM_TYPE_ALBUM, ALBUM_TYPE_SINGLE, ALBUM_TYPE_COMPILATION]:
            raise SpotifyComparatorException()
        if not 1900 < release_year < 2100:
            raise SpotifyComparatorException()
        if not 0 <= popularity <= 100:
            raise SpotifyComparatorException()
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

    return 10000 * compare_by_album_type + 1000 * compare_by_release_year + compare_by_album_popularity


def remove_parentheses(logger, elem):
    if '(' in elem:
        album_name_no_parentheses = elem.split(' (')[0]
        if should_print_changed_album_name_msg:
            logger.info('Changed album name', original_album_name=elem, changed_album_name=album_name_no_parentheses)
        return album_name_no_parentheses
    return elem


# if this function returns False, the track will remove
def filter_tracks(track, expected_track_name):
    try:
        track['album']['images'][0]["url"]
        return track['name'] == expected_track_name
    except:
        return False
