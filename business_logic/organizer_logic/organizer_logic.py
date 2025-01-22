import traceback
from typing import List, Tuple, Dict
from business_logic.albums_logic.albums_logic import AlbumsLogic
from entities.album import AlbumEntity
from entities.track import TrackEntity
from schemas.env_vars import EnvVars
from services.discogs.discogs_service import DiscogsService
from services.interfaces.fetch_tracks_info_service import FetchTracksInfoService
from services.mp3.mp3_service import MP3Service
from services.spotify.spotify_service import SpotifyService
from shared.constants import TITLE_TAG_NAME, ARTIST_TAG_NAME, ALBUM_NAME_TAG_NAME, TRACK_NUMBER_TAG_NAME, \
    TRACK_YEAR_TAG_NAME, DISC_NUM_TAG_NAME
from shared.logger import Logger


class OrganizerLogic:

    def __init__(self, logger: Logger, env_vars: EnvVars):
        self._logger = logger
        self._mp3_service: MP3Service = MP3Service(logger=logger)
        self._fetch_tracks_service: FetchTracksInfoService = SpotifyService(client_id=env_vars.SPOTIFY_CLIENT_ID,
                                                                            client_secret=env_vars.SPOTIFY_CLIENT_SECRET,
                                                                            logger=logger)
        self._albums_logic = AlbumsLogic(logger=logger)
        self._discogs_service = DiscogsService(api_key=env_vars.DISCOGS_API_KEY, api_secret=env_vars.DISCOGS_API_SECRET,
                                               logger=logger)

    def organize_songs(self, mp3_files: List[str]) -> Tuple[List[str], List[Dict]]:
        invalid_files = []
        modified_files = []
        for mp3_file_path in sorted(mp3_files):
            try:
                self._logger.debug(f"\n{'#' * 200}\nStarting organize song", mp3_file_path=mp3_file_path)
                self._mp3_service.init_tag_values(mp3_file_path=mp3_file_path)
                self._mp3_service.delete_unused_tags(mp3_file_path=mp3_file_path)
                artist, track = self._mp3_service.extract_artist_and_track_from_mp3(mp3_file_path=mp3_file_path)
                self._mp3_service.set_mp3_tag_value(mp3_file_path=mp3_file_path, tag_name=TITLE_TAG_NAME,
                                                    tag_value=track)
                self._mp3_service.set_mp3_tag_value(mp3_file_path=mp3_file_path, tag_name=ARTIST_TAG_NAME,
                                                    tag_value=artist)
                all_tracks: List[TrackEntity] = self._fetch_tracks_service.get_tracks(artist=artist, track=track)
                self._discogs_service.verify_albums(artist=artist, track=track, tracks=all_tracks)
                album_entity: AlbumEntity = self._albums_logic.get_best_album(artist=artist, track=track,
                                                                              all_tracks=all_tracks)
                old_album = self._mp3_service.get_mp3_tag_value(mp3_file_path=mp3_file_path,
                                                                tag_name=ALBUM_NAME_TAG_NAME)
                if old_album != album_entity.name:
                    modified_files.append(
                        {'file': mp3_file_path, 'old_album': old_album, 'new_album': album_entity.name})
                self._mp3_service.set_mp3_tag_value(mp3_file_path=mp3_file_path, tag_name=ALBUM_NAME_TAG_NAME,
                                                    tag_value=album_entity.name)
                self._mp3_service.set_mp3_tag_value(mp3_file_path=mp3_file_path, tag_name=TRACK_NUMBER_TAG_NAME,
                                                    tag_value=f'{album_entity.track_number}/{album_entity.total_tracks}')
                self._mp3_service.set_mp3_tag_value(mp3_file_path=mp3_file_path, tag_name=TRACK_YEAR_TAG_NAME,
                                                    tag_value=album_entity.release_date)
                self._mp3_service.set_mp3_tag_value(mp3_file_path=mp3_file_path, tag_name=DISC_NUM_TAG_NAME,
                                                    tag_value=str(album_entity.disc_number))
                self._mp3_service.set_mp3_cover(mp3_file_path=mp3_file_path, cover_url=album_entity.images[0].url)
            except Exception as e:
                invalid_files.append(mp3_file_path)
                if isinstance(e, ValueError):
                    continue
                self._logger.error('Error occurred when trying to organize song', mp3_file_path=mp3_file_path, error=e,
                                   trace=traceback.format_exc())
                continue
        return invalid_files, modified_files
