from mutagen.id3 import TIT2, TPE1, TALB, ID3, APIC
import requests
from shared.constants import TITLE_TAG_NAME, ARTIST_TAG_NAME, ALBUM_NAME_TAG_NAME, PRESERVED_TAGS, DEFAULT_TAG_VALUE
import re
from typing import Tuple
from shared.exceptions import Mp3ServiceException
from shared.logger import Logger

TAGS_CONSTRUCTORS_DICT = {TITLE_TAG_NAME: TIT2, ARTIST_TAG_NAME: TPE1, ALBUM_NAME_TAG_NAME: TALB}


class MP3Service:

    def __init__(self, logger: Logger):
        self._logger = logger

    def get_mp3_tag_value(self, mp3_file_path: str, tag_name: str) -> str:
        audio = ID3(mp3_file_path)
        return audio.get(tag_name).text[0] if tag_name in audio else None

    def set_mp3_tag_value(self, mp3_file_path: str, tag_name: str, tag_value: str) -> None:
        audio = ID3(mp3_file_path)
        audio.add(TAGS_CONSTRUCTORS_DICT[tag_name](encoding=3, text=tag_value))
        audio.save()

    def set_mp3_cover(self, mp3_file_path: str, cover_url: str) -> None:
        audio = ID3(mp3_file_path)
        image_data = requests.get(cover_url).content
        audio.add(APIC(3, 'image/jpeg', 3, '', image_data))
        audio.save()

    def delete_unused_tags(self, mp3_file_path: str) -> None:
        audio = ID3(mp3_file_path)
        for tag in list(audio.keys()):
            if tag not in PRESERVED_TAGS:
                del audio[tag]
        audio.save()

    def init_tag_values(self, mp3_file_path: str) -> None:
        for tag_name in [TITLE_TAG_NAME, ARTIST_TAG_NAME, ALBUM_NAME_TAG_NAME]:
            if not self.get_mp3_tag_value(mp3_file_path=mp3_file_path, tag_name=tag_name):
                self.set_mp3_tag_value(mp3_file_path=mp3_file_path, tag_name=tag_name, tag_value=DEFAULT_TAG_VALUE)

    def delete_all_tags(self, mp3_file_path: str) -> None:
        audio = ID3(mp3_file_path)
        for tag in list(audio.keys()):
            del audio[tag]
        audio.save()

    def extract_artist_and_track_from_mp3(self, mp3_file_path: str) -> Tuple[str, str]:
        file_name, file_name_no_extension, artist, track = None, None, None, None
        try:
            file_name = mp3_file_path.split("/")[-1]
            file_name_no_extension = file_name.split(".mp3")[0]
            artist, track = re.split(r' - | \u2013 ', file_name_no_extension)
            return artist.replace(':', '/'), track
        except Exception:
            self._logger.error('Invalid MP3 file name', mp3_file=mp3_file_path, file_name=file_name,
                               file_name_no_extension=file_name_no_extension, artist=artist, track=track)
            raise Mp3ServiceException()
