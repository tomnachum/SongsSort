from schemas.env_vars import EnvVars
from services.mp3.mp3_service import MP3Service
from shared.env_vars_factory import get_env_vars
from shared.get_mp3_files import get_mp3_files
from shared.logger import Logger


def organize_tags():
    env_vars: EnvVars = get_env_vars()
    logger = Logger(debug_enabled=env_vars.DEBUG)

    mp3_files: set[str] = get_mp3_files(songs_directory=f'../{env_vars.SONGS_DIRECTORY}', logger=logger)

    mp3_service: MP3Service = MP3Service(logger=logger)

    for mp3_file_path in sorted(mp3_files):
        mp3_service.delete_unused_tags(mp3_file_path=mp3_file_path)
        mp3_service.init_tag_values(mp3_file_path=mp3_file_path, logger=logger)


if __name__ == '__main__':
    organize_tags()