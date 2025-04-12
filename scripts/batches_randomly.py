import os
import shutil
import random
from schemas.env_vars import EnvVars
from shared.env_vars_factory import get_env_vars
from shared.get_mp3_files import get_mp3_files
from shared.logger import Logger

BATCH_SIZE = 200


def copy_mp3s_to_random_batches(output_dir: str, batch_size: int = BATCH_SIZE):
    env_vars: EnvVars = get_env_vars()
    logger = Logger(debug_enabled=env_vars.DEBUG)

    mp3_files = list(get_mp3_files(songs_directory=f'../{env_vars.SONGS_DIRECTORY}', logger=logger))

    random.shuffle(mp3_files)

    if os.path.exists(output_dir):
        print(f"Removing existing directory: {output_dir}")
        shutil.rmtree(output_dir)

    os.makedirs(output_dir)

    batch_index = 1
    for i in range(0, len(mp3_files), batch_size):
        batch = mp3_files[i:i + batch_size]
        batch_folder = os.path.join(output_dir, f"batch_{batch_index}")
        os.makedirs(batch_folder, exist_ok=True)

        for f in batch:
            shutil.copy2(f, batch_folder)

        print(f"Copied batch {batch_index} with {len(batch)} files.")
        batch_index += 1


if __name__ == '__main__':
    copy_mp3s_to_random_batches(output_dir='/Users/tomnachum/Desktop/Batches Randomly')
