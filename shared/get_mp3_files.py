from services.directory_utils.directory_utils import get_files_in_folder
from shared.logger import Logger


def get_mp3_files(songs_directory: str, logger: Logger) ->set[str]:
    all_files = get_files_in_folder(folder_path=songs_directory)
    mp3_files = get_files_in_folder(folder_path=songs_directory, files_type='.mp3')
    if len(all_files) > len(mp3_files):
        logger.error(f'Found non mp3 files in {songs_directory}',
                     non_mp3_files=all_files - mp3_files)
        exit(1)
    if len(mp3_files) == 0:
        logger.info('no np3 files found in directory', directory=songs_directory)
        exit(1)
    return mp3_files