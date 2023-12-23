import os
import shutil
from glob import glob
from typing import List

from business_logic.organizer_logic.organizer_logic import OrganizerLogic
from shared.logger import Logger
from schemas.env_vars import EnvVars
from shared.env_vars_factory import get_env_vars
from wraptimer import TimeIt


def get_files_in_folder(folder_path: str, files_type: str = '') -> set[str]:
    return set(f for f in glob(os.path.join(folder_path, '*' + files_type), recursive=False) if os.path.isfile(f))


def copy_files_to_test_folder(destination_folder_path: str, files: List[str]) -> None:
    os.makedirs(destination_folder_path, exist_ok=True)
    for invalid_file in files:
        file_name = os.path.basename(invalid_file)
        destination_path = os.path.join(destination_folder_path, file_name)
        shutil.copy2(invalid_file, destination_path)


@TimeIt().func
def main():
    env_vars: EnvVars = get_env_vars()
    logger = Logger(is_test=env_vars.IS_TEST)
    folder_path = env_vars.FOLDER_PATH if not env_vars.IS_TEST else env_vars.TEST_FOLDER_PATH

    all_files = get_files_in_folder(folder_path=folder_path)
    mp3_files = get_files_in_folder(folder_path=folder_path, files_type='.mp3')

    if len(all_files) > len(mp3_files):
        logger.error(f'Found non mp3 files in {env_vars.FOLDER_PATH}',
                     non_mp3_files=all_files - mp3_files)
        exit(1)

    mp3_files_no_live = list(filter(lambda f: '(Live)' not in f, mp3_files))

    organizer_logic = OrganizerLogic(logger=logger, env_vars=env_vars)
    invalid_files, modified_files = organizer_logic.organize_songs(mp3_files=mp3_files_no_live)

    if len(modified_files) > 0:
        logger.warning('Total modified files', total=len(modified_files))
        logger.warning('Modified files', modified_files=modified_files)
        if not env_vars.IS_TEST:
            m_files = list(map(lambda d: d['file'], modified_files))
            copy_files_to_test_folder(destination_folder_path=env_vars.MODIFIED_FOLDER_PATH,
                                      files=m_files)
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
        if not env_vars.IS_TEST:
            copy_files_to_test_folder(destination_folder_path=env_vars.INVALID_FOLDER_PATH,
                                      files=invalid_files)
        logger.error(f'Total invalid percentage = {(len(invalid_files) / (studio_files)) * 100}%')
    elif total_files > 0:
        logger.success('All tracks edited successfully!!')


if __name__ == '__main__':
    main()
