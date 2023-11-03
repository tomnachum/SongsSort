from typing import List
from entities.album import AlbumEntity
from entities.track import TrackEntity
import json
from unidecode import unidecode
from shared.logger import Logger


def tracks_to_json(all_tracks: List[TrackEntity]) -> str:
    return json.dumps(list(map(lambda track: (track.dict()), all_tracks)), indent=None, separators=(',', ':'))


class AlbumsLogic:
    def __init__(self, logger: Logger):
        self._logger = logger

    def get_best_album(self, artist: str, track: str, all_tracks: List[TrackEntity]) -> AlbumEntity:
        if len(all_tracks) <= 0:
            self._logger.error('No albums found', artist=artist, track=track)
            raise ValueError
        self._logger.test("\n" + tracks_to_json(all_tracks), total_tracks=len(all_tracks))

        filtered_tracks = filter(lambda t: self.filter_tracks(t, track, artist), all_tracks)
        sorted_tracks = sorted(filtered_tracks, key=self.tracks_comparator, reverse=True)

        if not sorted_tracks:
            self._logger.error('After sorting albums, 0 albums remained.', artist=artist, track=track)
            raise ValueError

        album = sorted_tracks[0].album
        if album.album_type != 'album':
            self._logger.info('Could not find studio album', artist=artist, track=track, found_type=album.album_type)

        if '(' in album.name:
            album_name_no_parentheses = album.name.split(' (')[0]
            self._logger.info('Changed album name', original=album.name, new=album_name_no_parentheses)
            album.name = album_name_no_parentheses

        return album

    # the best track gets the highest score
    def tracks_comparator(self, track: TrackEntity) -> int:
        if 'Various Artists' in [a.name for a in track.album.artists]:
            return 0
        # first sore by album type:
        # [1, 4] / -1
        # [0, 3] / :3
        # range [0, 1]
        type_score_dict = {"verified_album": 4, "album": 3, "single": 2, "compilation": 1}
        compare_by_album_type = (type_score_dict[track.album.album_type] - 1) / 3

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

    # if this function returns False, the track will be removed
    def filter_tracks(self, track: TrackEntity, expected_track_name: str = '',
                      expected_track_artist: str = '') -> bool:
        try:
            if not track.album or not track.album.images:
                self._logger.test("album not exists or picture not exist")
                return False
            if any((word.lower() in ['live', 'concert']) for word in track.name.split()) and \
                    all(('live' not in word.lower()) for word in expected_track_name.split()):
                self._logger.test("live or concert in album name", track_name_in_spotify=track.name)
                return False
            actual_artists = set([a.name for a in track.album.artists]) - {'Various Artists'}
            if actual_artists and all([(unidecode(expected_track_artist) not in unidecode(artist_name)
                                        and unidecode(artist_name) not in unidecode(expected_track_artist))
                                       for artist_name in actual_artists]):
                self._logger.test("artist not in album artists", album_artists=track.album.artists,
                                  expected_track_artist=expected_track_artist)
                return False
            if track.album.album_type == 'album' and track.album.total_tracks > 30 and track.popularity > 20:  # Probably compilation album
                self._logger.test("album has alot of songs and is popular", tracks=track.album.total_tracks,
                                  popularity=track.popularity)
                return False
            return True
        except Exception as e:
            self._logger.test('filter exception', error=e)
            return False
