import os
import shutil
from schemas.env_vars import EnvVars
from services.mp3.mp3_service import MP3Service
from shared.env_vars_factory import get_env_vars
from shared.get_mp3_files import get_mp3_files
from shared.logger import Logger

BATCH_SIZE = 200


def copy_mp3s_to_batches(output_dir:str, batch_size: int = BATCH_SIZE):
    env_vars: EnvVars = get_env_vars()
    logger = Logger(debug_enabled=env_vars.DEBUG)

    mp3_files = list(get_mp3_files(songs_directory=f'../{env_vars.SONGS_DIRECTORY}', logger=logger))

    mp3_files.sort(key=lambda file: file.lower().replace('-', '').strip())

    if os.path.exists(output_dir):
        print(f"Removing existing directory: {output_dir}")
        shutil.rmtree(output_dir)

    os.makedirs(output_dir)

    mp3_service: MP3Service = MP3Service(logger=logger)

    batch_index = 1
    batch_files = []
    last_artist = None

    for file in mp3_files:
        artist, track = mp3_service.extract_artist_and_track_from_mp3(mp3_file_path=file)

        if len(batch_files) >= batch_size and artist != last_artist:
            batch_folder = os.path.join(output_dir, f"batch_{batch_index}")
            os.makedirs(batch_folder, exist_ok=True)
            for f in batch_files:
                shutil.copy2(f, batch_folder)
            print(f"Copied batch {batch_index} with {len(batch_files)} files.")
            batch_files = []
            batch_index += 1

        batch_files.append(file)
        last_artist = artist

    if batch_files:
        batch_folder = os.path.join(output_dir, f"batch_{batch_index}")
        os.makedirs(batch_folder, exist_ok=True)
        for f in batch_files:
            shutil.copy2(f, batch_folder)
        print(f"Copied final batch {batch_index} with {len(batch_files)} files.")


if __name__ == '__main__':
    copy_mp3s_to_batches(output_dir='/Users/tomnachum/Desktop/Batches Alphabetically')
