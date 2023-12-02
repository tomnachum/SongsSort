from typing import List
from entities.album import AlbumEntity, AlbumType
from entities.track import TrackEntity, Score
import json
from unidecode import unidecode
from shared.logger import Logger


def tracks_to_json(all_tracks: List[TrackEntity]) -> str:
    return json.dumps(list(map(lambda track: (track.dict()), all_tracks)), indent=None, separators=(',', ':'))


ALBUM_TYPE_TO_SCORE = {AlbumType.VERIFIED_ALBUM: 3.4, AlbumType.ALBUM.value: 3,
                       AlbumType.SINGLE.value: 2, AlbumType.COMPILATION.value: 1}


class AlbumsLogic:
    def __init__(self, logger: Logger):
        self._logger = logger

    def get_best_album(self, artist: str, track: str, all_tracks: List[TrackEntity]) -> AlbumEntity:
        self._logger.test("All tracks before filtering:\n" + tracks_to_json(all_tracks), total_tracks=len(all_tracks))

        filtered_tracks = filter(lambda t: self.filter_tracks(t, track, artist), all_tracks)

        if not filtered_tracks:
            self._logger.error('After filtering albums, 0 albums remained.', artist=artist, track=track)
            raise ValueError

        sorted_tracks = sorted(filtered_tracks, key=self.tracks_comparator, reverse=True)

        self._logger.test("All tracks after filtering:\n" + tracks_to_json(sorted_tracks),
                          total_tracks=len(sorted_tracks))

        if not sorted_tracks:
            self._logger.error('After sorting albums, 0 albums remained.', artist=artist, track=track)
            raise ValueError

        track_entity = sorted_tracks[0]
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
        if 'Anniversary' in track.album.name or '(Deluxe Edition)' in track.album.name or 'Various Artists' in [a.name
                                                                                                                for a in
                                                                                                                track.album.artists]:
            return 0
        if track.album.album_type == 'album' and track.album.total_tracks > 30 and track.popularity > 20:  # Probably compilation album
            self._logger.test("album has alot of songs and is popular", album=track.album.model_dump())
            track.album.album_type = 'compilation'

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
                self._logger.test("album not exists or picture not exist")
                return False
            if any((word.lower() in ['live', 'concert', 'karaoke']) for word in
                   track.album.name.replace('(', '').replace(')', '').replace('[', '').replace(']', '').replace(',',
                                                                                                                '').split()) and \
                    all(('live' not in word.lower()) for word in expected_track_name.split()):
                self._logger.test("live or concert in album name", album_name=track.album.name,
                                  track_name_in_spotify=track.name, expected_track_name=expected_track_name)
                return False
            actual_artists = list(set([a.name for a in track.album.artists]) - {'Various Artists'})
            if actual_artists and len(actual_artists) > 1 and all(
                    [(unidecode(expected_track_artist) not in unidecode(artist_name)
                      and unidecode(artist_name) not in unidecode(expected_track_artist))
                     for artist_name in actual_artists]):
                self._logger.test("artist not in album artists", album_name=track.album.name,
                                  album_artists=actual_artists, expected_track_artist=f'{expected_track_artist}.')
                return False
            if actual_artists and len(actual_artists) == 1 and unidecode(actual_artists[0]) != unidecode(
                    expected_track_artist):
                self._logger.test("artist is not equal to album artist", album_name=track.album.name,
                                  album_artists=actual_artists, expected_track_artist=f'{expected_track_artist}.')
                if unidecode(expected_track_artist) not in unidecode(actual_artists[0]):
                    self._logger.test("artist is not even included in album artist", album_name=track.album.name,
                                      album_artists=actual_artists, expected_track_artist=f'{expected_track_artist}.')
                    return False
            if track.name.lower() != expected_track_name.lower() and expected_track_name not in track.name:
                self._logger.test("track name is not expected track name", album_name=track.album.name,
                                  track_name_in_spotify=track.name,
                                  expected_track_name=expected_track_name)
                return False
            return True
        except Exception as e:
            self._logger.test('filter exception', error=e)
            return False
