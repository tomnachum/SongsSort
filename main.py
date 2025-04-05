

from business_logic.organizer_logic.organizer_logic import OrganizerLogic
from services.directory_utils.directory_utils import copy_files_to_folder, create_folder_in_directory
from shared.get_mp3_files import get_mp3_files
from shared.logger import Logger
from schemas.env_vars import EnvVars
from shared.env_vars_factory import get_env_vars
from wraptimer import TimeIt


@TimeIt().func
def main():
    env_vars: EnvVars = get_env_vars()
    logger = Logger(debug_enabled=env_vars.DEBUG)

    mp3_files = get_mp3_files(songs_directory=env_vars.SONGS_DIRECTORY, logger=logger)

    mp3_files_no_live = list(filter(lambda f: '(Live)' not in f, mp3_files))

    organizer_logic = OrganizerLogic(logger=logger, env_vars=env_vars)
    invalid_files, modified_files = organizer_logic.organize_songs(mp3_files=mp3_files_no_live)

    if len(modified_files) > 0:
        logger.warning('Total modified files', total=len(modified_files))
        logger.warning('Modified files', modified_files=modified_files)
        m_files = list(map(lambda d: d['file'], modified_files))
        modified_folder_path = create_folder_in_directory(directory=env_vars.SONGS_DIRECTORY,folder_to_create='modified')
        copy_files_to_folder(destination_folder_path=modified_folder_path, files=m_files)
    else:
        logger.warning('No files were modified')

    total_files = len(mp3_files)
    live_files = len(mp3_files) - len(mp3_files_no_live)
    studio_files = total_files - live_files
    logger.success(f'Total files {total_files}')
    logger.success(f'Live files {live_files}')
    if len(invalid_files) > 0:
        logger.error(f'Total invalid files = {len(invalid_files)} / {studio_files}')
        logger.error(f'Invalid files', invalid_files=invalid_files)
        invalid_folder_path = create_folder_in_directory(directory=env_vars.SONGS_DIRECTORY,folder_to_create='invalid')
        copy_files_to_folder(destination_folder_path=invalid_folder_path, files=invalid_files)
        logger.error(f'Total invalid percentage = {(len(invalid_files) / (studio_files)) * 100}%')
    elif total_files > 0:
        logger.success('All tracks edited successfully!!')


if __name__ == '__main__':
    main()
