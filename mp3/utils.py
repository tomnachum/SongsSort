import re
from mp3.exceptions import Mp3HandlerException


def extract_artist_and_track_from_mp3(logger, mp3_file_path):
    file_name, file_name_no_extension, artist_name, track_name = None, None, None, None
    try:
        file_name = mp3_file_path.split("/")[-1]
        file_name_no_extension = file_name.split(".mp3")[0]
        artist_name, track_name = re.split(r' - | \u2013 ', file_name_no_extension)
        return artist_name.replace(':', '/'), track_name
    except Exception:
        logger.error('Invalid MP3 file name', mp3_file=mp3_file_path, file_name=file_name,
                     file_name_no_extension=file_name_no_extension, artist_name=artist_name, track_name=track_name)
        raise Mp3HandlerException()
