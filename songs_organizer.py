import os
import glob
from mp3.constants import TITLE_TAG_NAME, ARTIST_TAG_NAME, ALBUM_NAME_TAG_NAME
from mp3.exceptions import Mp3HandlerException
from mp3.mp3_handler import set_mp3_cover, init_tag_values, delete_all_tags, print_all_tags, delete_unused_tags, \
    set_mp3_tag_value
from mp3.utils import extract_artist_and_track_from_mp3
from spotify.spotify_api_handler import get_album_from_spotify, SpotifyException, get_spotify_token
from utils.logger import Logger
import time
import datetime
from dotenv import load_dotenv


def print_results(logger, invalid_files, total_files, live_files, total_time):
    logger.success(f'\nTotal files {total_files}')
    logger.success(f'Total time {total_time}')
    logger.success(f'Live files {live_files}')
    if invalid_files > 0:
        logger.error(f'Total invalid files = {invalid_files} / {total_files - live_files}')
    elif total_files > 0:
        logger.success('All tracks edited successfully!!')


if __name__ == '__main__':
    load_dotenv()
    is_test = bool(os.getenv('IS_TEST'))
    folder_path = os.getenv('FOLDER_PATH')
    client_id = os.getenv('CLIENT_ID')
    client_secret = os.getenv('CLIENT_SECRET')

    token = get_spotify_token(client_id=client_id, client_secret=client_secret)
    start_time = time.time()
    logger = Logger(is_test=is_test)
    mp3_files = glob.glob(os.path.join(folder_path, '*.mp3'))
    invalid_files = 0
    live_files = 0
    for mp3_file_path in sorted(mp3_files):
        logger.test(f"\n{'#' * 200}\nStarting organize song", mp3_file_path=mp3_file_path)
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
                                                           track_name=track_name, token=token)
            set_mp3_tag_value(mp3_file_path=mp3_file_path, tag_name=ALBUM_NAME_TAG_NAME, tag_value=album_name)
            set_mp3_cover(mp3_file_path=mp3_file_path, cover_url=cover_url)
        except (Mp3HandlerException, SpotifyException, KeyboardInterrupt):
            invalid_files += 1
            continue
        except Exception as e:
            logger.error('Error occurred when trying to organize song', mp3_file_path=mp3_file_path, error=e)
            invalid_files += 1
            continue
    end_time = time.time()
    total_time = datetime.timedelta(seconds=end_time - start_time)
    print_results(logger=logger, invalid_files=invalid_files, total_files=len(mp3_files), live_files=live_files,
                  total_time=total_time)
