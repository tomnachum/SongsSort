from typing import Dict

from spotify.utils import spotify_tracks_comparator


def create_track(album_type: str, release_date: str, popularity: int) -> Dict:
    return {
        "album": {
            "album_type": album_type,
            "release_date": release_date
        },
        "popularity": popularity
    }


class TestComparator:

    def test_sort_by_album_type(self):
        t1 = create_track(album_type='album', release_date='2000', popularity=30)
        t2 = create_track(album_type='single', release_date='2000', popularity=30)
        t3 = create_track(album_type='compilation', release_date='2000', popularity=30)
        tracks = [t3, t2, t1]
        sorted_tracks = sorted(tracks, key=spotify_tracks_comparator, reverse=True)
        assert sorted_tracks == [t1, t2, t3]

    def test_sort_by_release_date(self):
        t1 = create_track(album_type='album', release_date='1970', popularity=30)
        t2 = create_track(album_type='album', release_date='2000', popularity=30)
        t3 = create_track(album_type='album', release_date='2005', popularity=30)
        t4 = create_track(album_type='single', release_date='2000', popularity=30)
        tracks = [t3, t1, t4, t2]
        sorted_tracks = sorted(tracks, key=spotify_tracks_comparator, reverse=True)
        assert sorted_tracks == [t1, t2, t3, t4]

    def test_sort_by_popularity(self):
        t1 = create_track(album_type='album', release_date='1970', popularity=40)
        t2 = create_track(album_type='album', release_date='1970', popularity=30)
        t3 = create_track(album_type='album', release_date='1971', popularity=100)
        t4 = create_track(album_type='album', release_date='1972', popularity=80)
        t5 = create_track(album_type='album', release_date='2005', popularity=30)
        t6 = create_track(album_type='single', release_date='2000', popularity=30)
        t7 = create_track(album_type='compilation', release_date='1905', popularity=99)
        tracks = [t6, t2, t7, t3, t1, t5, t4]
        sorted_tracks = sorted(tracks, key=spotify_tracks_comparator, reverse=True)
        expected_sorted_tracks = [t1, t2, t3, t4, t5, t6, t7]
        assert sorted_tracks == expected_sorted_tracks
