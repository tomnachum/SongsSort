from mutagen.id3 import TIT2, TPE1, TALB, ID3, APIC, TRCK, TDRC, TPOS
import requests
from shared.constants import TITLE_TAG_NAME, ARTIST_TAG_NAME, ALBUM_NAME_TAG_NAME, PRESERVED_TAGS, DEFAULT_TAG_VALUE, \
    TRACK_NUMBER_TAG_NAME, TRACK_YEAR_TAG_NAME, DISC_NUM_TAG_NAME, TAGS_MEANING, TAGS_DEFAULT_VALUES, \
    TAGS_TO_BE_INITIALIZE
import re
from typing import Tuple
from shared.logger import Logger

TAGS_CONSTRUCTORS_DICT = {TITLE_TAG_NAME: TIT2, ARTIST_TAG_NAME: TPE1, ALBUM_NAME_TAG_NAME: TALB,
                          TRACK_NUMBER_TAG_NAME: TRCK, TRACK_YEAR_TAG_NAME: TDRC, DISC_NUM_TAG_NAME: TPOS}


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

    def init_tag_values(self, mp3_file_path: str, logger: Logger = None) -> None:
        for tag_name in TAGS_TO_BE_INITIALIZE:
            tag_value = self.get_mp3_tag_value(mp3_file_path=mp3_file_path, tag_name=tag_name)

            new_val = None
            if not tag_value:
                new_val = TAGS_DEFAULT_VALUES.get(tag_name)
            elif tag_name == DISC_NUM_TAG_NAME and len(tag_value) > 2:
                new_val = tag_value.split('/')[0]
            elif tag_name == DISC_NUM_TAG_NAME and int(tag_value) > 3:
                new_val = '1'
            elif tag_name == TRACK_NUMBER_TAG_NAME and len(tag_value) == 1:
                new_val = f'{tag_value}/0'

            if new_val:
                self.set_mp3_tag_value(mp3_file_path=mp3_file_path, tag_name=tag_name, tag_value=new_val)
                if logger: logger.info('set new tag for song', mp3_file_path=mp3_file_path, tag=TAGS_MEANING.get(tag_name), old_val=tag_value, new_value=new_val)

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
            hyphen_split_arr = re.split(r' - | \u2013 ', file_name_no_extension)
            artist = hyphen_split_arr[0]
            track = ' - '.join(hyphen_split_arr[1:])

            if len(artist.strip()) != len(artist):
                self._logger.error("String should not have spaces at the beginning.", mp3_file=mp3_file_path,
                                   file_name=file_name,
                                   file_name_no_extension=file_name_no_extension, artist=artist, track=track)
                raise ValueError()

            if len(track.strip()) != len(track):
                self._logger.error("String should not have spaces at the end.", mp3_file=mp3_file_path,
                                   file_name=file_name,
                                   file_name_no_extension=file_name_no_extension, artist=artist, track=track)
                raise ValueError()

            return artist.replace(':', '/'), track.replace(':', '/')
        except Exception as err:
            self._logger.error('Invalid MP3 file name', err=err, mp3_file=mp3_file_path, file_name=file_name,
                               file_name_no_extension=file_name_no_extension, artist=artist, track=track)
            raise ValueError
