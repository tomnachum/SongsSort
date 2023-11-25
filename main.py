import os
import glob
from business_logic.organizer_logic.organizer_logic import OrganizerLogic
from shared.logger import Logger
from schemas.env_vars import EnvVars
from shared.env_vars_factory import get_env_vars
from wraptimer import TimeIt


@TimeIt().func
def main():
    env_vars: EnvVars = get_env_vars()
    logger = Logger(is_test=env_vars.IS_TEST)
    all_files = set(glob.glob(os.path.join(env_vars.FOLDER_PATH, '*')))
    mp3_files = set(glob.glob(os.path.join(env_vars.FOLDER_PATH, '*.mp3')))

    if len(all_files) > len(mp3_files):
        logger.error(f'Found non mp3 files in {env_vars.FOLDER_PATH}',
                     non_mp3_files=all_files - mp3_files)
        exit(1)

    mp3_files_no_live = list(filter(lambda f: '(Live)' not in f, mp3_files))

    organizer_logic = OrganizerLogic(logger=logger, env_vars=env_vars)
    invalid_files = organizer_logic.organize_songs(mp3_files=mp3_files_no_live)

    total_files = len(mp3_files)
    live_files = len(mp3_files) - len(mp3_files_no_live)
    logger.success(f'\nTotal files {total_files}')
    logger.success(f'Live files {live_files}')
    if invalid_files > 0:
        logger.error(f'Total invalid files = {invalid_files} / {total_files - live_files}')
        logger.error(f'Total invalid percentage = {(invalid_files / (total_files - live_files)) * 100}%')
    elif total_files > 0:
        logger.success('All tracks edited successfully!!')


if __name__ == '__main__':
    main()
