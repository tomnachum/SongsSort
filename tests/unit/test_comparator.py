import pytest

from business_logic.albums_logic.albums_logic import AlbumsLogic
from entities.album import AlbumEntity
from entities.track import TrackEntity
from shared.logger import Logger


def create_track(album_type: str, release_date: str, popularity: int) -> TrackEntity:
    return TrackEntity(
        album=AlbumEntity(
            album_type=album_type,
            release_date=release_date,
            images=[],
            artists=[],
            total_tracks=4,
            name='test_album'
        ),
        popularity=popularity,
        name='test'
    )


@pytest.fixture(scope='module')
def tracks_comparator():
    logger = Logger(debug_enabled=True)
    albums_logic: AlbumsLogic = AlbumsLogic(logger=logger)
    return albums_logic.tracks_comparator


class TestComparator:

    def test_sort_by_album_type(self, tracks_comparator):
        t1 = create_track(album_type='album', release_date='2000', popularity=30)
        t2 = create_track(album_type='single', release_date='2000', popularity=30)
        t3 = create_track(album_type='compilation', release_date='2000', popularity=30)
        tracks = [t3, t2, t1]
        sorted_tracks = sorted(tracks, key=tracks_comparator, reverse=True)
        assert sorted_tracks == [t1, t2, t3]

    def test_sort_by_release_date(self, tracks_comparator):
        t1 = create_track(album_type='album', release_date='1970', popularity=30)
        t2 = create_track(album_type='album', release_date='2000', popularity=30)
        t3 = create_track(album_type='album', release_date='2005', popularity=30)
        t4 = create_track(album_type='single', release_date='2000', popularity=30)
        tracks = [t3, t1, t4, t2]
        sorted_tracks = sorted(tracks, key=tracks_comparator, reverse=True)
        assert sorted_tracks == [t1, t2, t3, t4]

    def test_sort_by_popularity(self, tracks_comparator):
        t1 = create_track(album_type='album', release_date='1970', popularity=40)
        t2 = create_track(album_type='album', release_date='1970', popularity=30)
        t3 = create_track(album_type='album', release_date='1971', popularity=100)
        t4 = create_track(album_type='album', release_date='1972', popularity=80)
        t5 = create_track(album_type='album', release_date='2005', popularity=30)
        t6 = create_track(album_type='single', release_date='2000', popularity=30)
        t7 = create_track(album_type='compilation', release_date='1905', popularity=99)
        tracks = [t6, t2, t7, t3, t1, t5, t4]
        sorted_tracks = sorted(tracks, key=tracks_comparator, reverse=True)
        expected_sorted_tracks = [t1, t2, t3, t4, t5, t6, t7]
        assert sorted_tracks == expected_sorted_tracks
