from mp3.exceptions import Mp3HandlerException


def extract_artist_and_track_from_mp3(logger, mp3_file_path):
    try:
        return mp3_file_path.split("/")[-1].split(".mp3")[0].split(' - ')
    except Exception:
        logger.error('Invalid MP3 file name', mp3_file=mp3_file_path)
        raise Mp3HandlerException()
