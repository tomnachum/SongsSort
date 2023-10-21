from mutagen.id3 import TIT2, TPE1, TALB, ID3, APIC
import requests
from mp3.constants import *

TAGS_CONSTRUCTORS_DICT = {TITLE_TAG_NAME: TIT2, ARTIST_TAG_NAME: TPE1, ALBUM_NAME_TAG_NAME: TALB}


def get_mp3_tag_value(mp3_file_path: str, tag_name: str) -> str:
    audio = ID3(mp3_file_path)
    return audio.get(tag_name).text[0] if tag_name in audio else None


def set_mp3_tag_value(mp3_file_path: str, tag_name: str, tag_value: str) -> None:
    audio = ID3(mp3_file_path)
    audio.add(TAGS_CONSTRUCTORS_DICT[tag_name](encoding=3, text=tag_value))
    audio.save()


def set_mp3_cover(mp3_file_path: str, cover_url: str) -> None:
    audio = ID3(mp3_file_path)
    image_data = requests.get(cover_url).content
    audio.add(APIC(3, 'image/jpeg', 3, '', image_data))
    audio.save()


def delete_unused_tags(mp3_file_path: str) -> None:
    audio = ID3(mp3_file_path)
    for tag in list(audio.keys()):
        if tag not in PRESERVED_TAGS:
            del audio[tag]
    audio.save()


def init_tag_values(mp3_file_path: str) -> None:
    for tag_name in [TITLE_TAG_NAME, ARTIST_TAG_NAME, ALBUM_NAME_TAG_NAME]:
        if not get_mp3_tag_value(mp3_file_path=mp3_file_path, tag_name=tag_name):
            set_mp3_tag_value(mp3_file_path=mp3_file_path, tag_name=tag_name, tag_value=DEFAULT_TAG_VALUE)


def delete_all_tags(mp3_file_path: str) -> None:
    audio = ID3(mp3_file_path)
    for tag in list(audio.keys()):
        del audio[tag]
    audio.save()


def print_all_tags(mp3_file_path: str) -> None:
    audio = ID3(mp3_file_path)
    print(list(audio.keys()))
