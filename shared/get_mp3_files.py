from services.directory_utils.directory_utils import get_files_in_folder


def get_mp3_files(env_vars, logger) ->set[str]:
    all_files = get_files_in_folder(folder_path=f'../{env_vars.SONGS_DIRECTORY}')
    mp3_files = get_files_in_folder(folder_path=f'../{env_vars.SONGS_DIRECTORY}', files_type='.mp3')
    if len(all_files) > len(mp3_files):
        logger.error(f'Found non mp3 files in {env_vars.SONGS_DIRECTORY}',
                     non_mp3_files=all_files - mp3_files)
        exit(1)
    if len(mp3_files) == 0:
        logger.info('no np3 files found in directory', directory=env_vars.SONGS_DIRECTORY)
        exit(1)
    return mp3_files