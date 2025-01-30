from typing import List
from entities.album import AlbumEntity, AlbumType
from entities.track import TrackEntity, Score
import json
from unidecode import unidecode
from shared.logger import Logger
from typing import Dict

def print_track(track: TrackEntity):
    return (json.dumps({
        'track_name': track.name,
        'album_name': track.album.name,
        'score': track.score.model_dump_json() if track.score else {},
        'artwork': track.album.images[0].url
    }, indent=4))


def format_tracks(all_tracks: List[TrackEntity]):
    # return json.dumps(list(map(lambda track: (track.dict()), all_tracks)), indent=None, separators=(',', ':'))
    return [print_track(track=track) for track in all_tracks]


ALBUM_TYPE_TO_SCORE = {AlbumType.VERIFIED_ALBUM: 3.4, AlbumType.ALBUM.value: 3,
                       AlbumType.SINGLE.value: 2, AlbumType.COMPILATION.value: 1, AlbumType.SOUNDTRACK.value: 3.2
                       }

BANNED_ALBUM_KEYWORDS = ['(Super Deluxe Edition)', 'Anniversary', '(Deluxe Edition)']

class AlbumsLogic:
    def __init__(self, logger: Logger):
        self._logger = logger

    def get_best_album(self, artist: str, track: str, all_tracks: List[TrackEntity]) -> AlbumEntity:
        self._logger.debug("All tracks:", tracks=format_tracks(all_tracks), total_tracks=len(all_tracks))

        filtered_tracks = filter(lambda t: self.filter_tracks(t, track, artist), all_tracks)

        if not filtered_tracks:
            self._logger.error('After filtering albums, 0 albums remained.', artist=artist, track=track)
            raise ValueError

        sorted_tracks = sorted(filtered_tracks, key=self.tracks_comparator, reverse=True)

        album_name_tracks_mapping: Dict[str, TrackEntity] = {}
        for track in sorted_tracks:
            if track.album.name in album_name_tracks_mapping:
                album_name_tracks_mapping[track.album.name].score.total +=1
            else:
                album_name_tracks_mapping[track.album.name] = track

        unique_tracks = sorted(list(album_name_tracks_mapping.values()), key=lambda track: track.score.total, reverse=True)

        self._logger.debug("All tracks after filtering and sorting:", tracks = format_tracks(unique_tracks),
                           total_tracks=len(unique_tracks))

        if not unique_tracks:
            self._logger.error('After sorting albums, 0 albums remained.', artist=artist, track=track)
            raise ValueError

        track_entity = unique_tracks[0]
        album = track_entity.album
        if album.album_type != AlbumType.ALBUM and album.album_type != AlbumType.VERIFIED_ALBUM:
            self._logger.info('Could not find studio album', artist=artist, track=track, found_type=album.album_type)

        if '(' in album.name:
            album_name_no_parentheses = album.name.split(' (')[0]
            if all(word not in album.name for word in
                   ['Remastered', 'Delux', 'Expanded', 'New', 'Remaster', 'Edition', 'Mix']):
                self._logger.info('Changed album name', original=album.name, new=album_name_no_parentheses,
                                  artist=artist,
                                  track=track)
            album.name = album_name_no_parentheses

        return album

    # the best track gets the highest score
    def tracks_comparator(self, track: TrackEntity) -> float:
        if track.album.album_type == 'album' and track.album.total_tracks > 30 and track.popularity > 20:
            self._logger.debug("album has alot of songs and is popular, Probably compilation album", album=track.album.model_dump())
            track.album.album_type = 'compilation'

        if 'Soundtrack' in track.album.name:
            track.album.album_type = 'soundtrack'



        # first sore by album type:
        # [1, 2, 3, 3.4]
        # [100, 200, 300, 340]
        compare_by_album_type = ALBUM_TYPE_TO_SCORE[track.album.album_type] * 100

        # then sort by release year
        # lowest is better score
        # 2020 - [1920, 2020]
        # [100,...,0]
        compare_by_release_year = 2020 - int(track.album.release_date)

        # then sort by popularity
        # [0,...,100]
        compare_by_album_popularity = track.popularity

        if any(banned_keyword in track.album.name for banned_keyword in BANNED_ALBUM_KEYWORDS) or 'Acoustic' in track.name:
            compare_by_album_type -= 100
        if 'Various Artists' in [a.name for a in track.album.artists]:
            compare_by_album_type -= 100
            compare_by_album_popularity = 0

        score = 10 * compare_by_album_type + 15 * compare_by_release_year + compare_by_album_popularity
        track.score = Score(album_type=compare_by_album_type,
                            release_year=compare_by_release_year,
                            popularity=compare_by_album_popularity,
                            total=score)

        return score

    # if this function returns False, the track will be removed
    def filter_tracks(self, track: TrackEntity, expected_track_name: str = '', expected_track_artist: str = '') -> bool:
        try:
            if not track.album or not track.album.images:
                # self._logger.debug("album not exists or picture not exist")
                return False
            album_name_no_special_chars = ''.join(
                char for char in track.album.name if char not in ['(', ')', '[', ']', ',', "'"])
            album_include_forbidden_word = any((word.lower() in ['live', 'concert', 'karaoke', 'tribute']) for word in
                   album_name_no_special_chars.split())
            track_is_not_live = all(('live' != word.lower()) for word in expected_track_name.split())
            if album_include_forbidden_word and track_is_not_live:
                # self._logger.debug("banned name in album name", album_name=track.album.name,
                #                    track_name_in_spotify=track.name, expected_track_name=expected_track_name)
                return False
            actual_artists = list(set([a.name for a in track.album.artists]) - {'Various Artists'})
            if actual_artists and len(actual_artists) > 1 and all(
                    [(unidecode(expected_track_artist) not in unidecode(artist_name)
                      and unidecode(artist_name) not in unidecode(expected_track_artist))
                     for artist_name in actual_artists]):
                # self._logger.debug("artist not in album artists", album_name=track.album.name,
                #                    album_artists=actual_artists, expected_track_artist=f'{expected_track_artist}.')
                return False
            if actual_artists and len(actual_artists) == 1 and unidecode(actual_artists[0]) != unidecode(
                    expected_track_artist):
                if 'Tribute' in actual_artists[0]:
                    # self._logger.debug("Tribute in artist", album_name=track.album.name,
                    #                    album_artists=actual_artists, expected_track_artist=f'{expected_track_artist}.')
                    return False
                # self._logger.debug("artist is not equal to album artist", album_name=track.album.name,
                #                    album_artists=actual_artists, expected_track_artist=f'{expected_track_artist}.')
                if unidecode(expected_track_artist) not in unidecode(actual_artists[0]):
                    # self._logger.debug("artist is not even included in album artist", album_name=track.album.name,
                    #                    album_artists=actual_artists, expected_track_artist=f'{expected_track_artist}.')
                    return False
            if 'live' in [word.lower() for word in track.name.split()] and \
                    'live' not in [word.lower() for word in expected_track_name.split()]:
                # self._logger.debug("live in track name", album_name=track.album.name,
                #                    track_name_in_spotify=track.name,
                #                    expected_track_name=expected_track_name)
                return False
            if unidecode(track.name.lower()) != unidecode(expected_track_name.lower()) and unidecode(
                    expected_track_name.lower()) not in unidecode(track.name.lower()):
                # self._logger.debug("track name is not expected track name", album_name=track.album.name,
                #                    track_name_in_spotify=track.name,
                #                    expected_track_name=expected_track_name)
                return False
            return True
        except Exception as e:
            self._logger.debug('filter exception', error=e)
            return False
