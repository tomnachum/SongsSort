import os
import glob
from config.configurations import is_test, should_print_start_msg
from constants import TEST_FOLDER_PATH, SORT_FOLDER_PATH
from mp3.constants import TITLE_TAG_NAME, ARTIST_TAG_NAME, ALBUM_NAME_TAG_NAME
from mp3.exceptions import Mp3HandlerException
from mp3.mp3_handler import set_mp3_cover, init_tag_values, delete_all_tags, print_all_tags, delete_unused_tags, \
    set_mp3_tag_value
from mp3.utils import extract_artist_and_track_from_mp3
from spotify.spotify_api_handler import get_album_from_spotify, SpotifyException
from utils.logger import Logger


def print_results(logger, invalid_files, total_files, live_files):
    logger.success(f'\nTotal files {total_files}')
    logger.success(f'Live files {live_files}')
    if invalid_files > 0:
        logger.error(f'Total invalid files = {invalid_files} / {total_files - live_files}')
    elif total_files > 0:
        logger.success('All tracks edited successfully!!')


if __name__ == '__main__':
    logger = Logger()
    folder_path = TEST_FOLDER_PATH if is_test else SORT_FOLDER_PATH
    mp3_files = glob.glob(os.path.join(folder_path, '*.mp3'))
    invalid_files = 0
    live_files = 0
    for mp3_file_path in sorted(mp3_files):
        if should_print_start_msg or is_test:
            print("\n" + ("#" * 200) + "\n")
            logger.info(f"Starting organize song", mp3_file_path=mp3_file_path)
        init_tag_values(mp3_file_path=mp3_file_path)
        delete_unused_tags(mp3_file_path=mp3_file_path)
        if '(Live)' in mp3_file_path:
            live_files += 1
            continue
        try:
            artist_name, track_name = extract_artist_and_track_from_mp3(logger=logger, mp3_file_path=mp3_file_path)
            set_mp3_tag_value(mp3_file_path=mp3_file_path, tag_name=TITLE_TAG_NAME, tag_value=track_name)
            set_mp3_tag_value(mp3_file_path=mp3_file_path, tag_name=ARTIST_TAG_NAME, tag_value=artist_name)
            album_name, cover_url = get_album_from_spotify(logger=logger, artist_name=artist_name,
                                                           track_name=track_name)
            set_mp3_tag_value(mp3_file_path=mp3_file_path, tag_name=ALBUM_NAME_TAG_NAME, tag_value=album_name)
            set_mp3_cover(mp3_file_path=mp3_file_path, cover_url=cover_url)
        except (Mp3HandlerException, SpotifyException, KeyboardInterrupt):
            invalid_files += 1
            continue
        except Exception as e:
            logger.error('Error occurred when trying to organize song', mp3_file_path=mp3_file_path, error=e)
            invalid_files += 1
            continue

    print_results(logger=logger, invalid_files=invalid_files, total_files=len(mp3_files), live_files=live_files)
