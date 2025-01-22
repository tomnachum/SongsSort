import os
import shutil
from glob import glob
from typing import List


def create_folder_in_directory(directory: str, folder_to_create: str) -> str:
    parent_dir = os.path.dirname(directory)
    songs_sort_debugging_path = os.path.join(parent_dir, "SongsSortDebugging")
    folder_to_create_path = os.path.join(songs_sort_debugging_path, folder_to_create)
    if not os.path.exists(songs_sort_debugging_path):
        os.makedirs(songs_sort_debugging_path)
    if not os.path.exists(folder_to_create_path):
        os.makedirs(folder_to_create_path)
    return folder_to_create_path


def get_files_in_folder(folder_path: str, files_type: str = '') -> set[str]:
    return set(f for f in glob(os.path.join(folder_path, '*' + files_type), recursive=False) if os.path.isfile(f))


def copy_files_to_folder(destination_folder_path: str, files: List[str]) -> None:
    os.makedirs(destination_folder_path, exist_ok=True)
    for invalid_file in files:
        file_name = os.path.basename(invalid_file)
        destination_path = os.path.join(destination_folder_path, file_name)
        shutil.copy2(invalid_file, destination_path)