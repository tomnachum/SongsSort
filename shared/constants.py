DISCOGS_URL = 'https://api.discogs.com/database/search'

DEFAULT_TAG_VALUE = 'None'

TITLE_TAG_NAME = 'TIT2'

ARTIST_TAG_NAME = 'TPE1'

ALBUM_NAME_TAG_NAME = 'TALB'

# This is both track_number tag and total_tracks tag. the format value for the tag is track_number/total_tracks
TRACK_NUMBER_TAG_NAME = 'TRCK'

TRACK_YEAR_TAG_NAME = 'TDRC'

# This is both disc_num tag and total_discs tag. the format value for the tag is disc_num/total_discs
# if the value we provide is only 1 for example (and not 1/1), total_discs tag will not be initilize
DISC_NUM_TAG_NAME = 'TPOS'

TAGS_TO_BE_INITIALIZE = [TITLE_TAG_NAME, ARTIST_TAG_NAME, ALBUM_NAME_TAG_NAME, TRACK_NUMBER_TAG_NAME, TRACK_YEAR_TAG_NAME, DISC_NUM_TAG_NAME]

ALBUM_COVER_TAG_NAME = 'APIC:'

TAGS_MEANING = {
 TITLE_TAG_NAME: 'Title',
 ARTIST_TAG_NAME: 'Artist',
 ALBUM_NAME_TAG_NAME: 'Album',
 TRACK_NUMBER_TAG_NAME: 'Track number',
 TRACK_YEAR_TAG_NAME: 'Year',
 DISC_NUM_TAG_NAME:'Disc Num',
 ALBUM_COVER_TAG_NAME: 'Album Cover'
}

TAGS_DEFAULT_VALUES = {
 TITLE_TAG_NAME: DEFAULT_TAG_VALUE,
 ARTIST_TAG_NAME: DEFAULT_TAG_VALUE,
 ALBUM_NAME_TAG_NAME: DEFAULT_TAG_VALUE,
 TRACK_NUMBER_TAG_NAME: '0/0',
 TRACK_YEAR_TAG_NAME: '1900',
 DISC_NUM_TAG_NAME: '1',
 ALBUM_COVER_TAG_NAME: DEFAULT_TAG_VALUE
}

PRESERVED_TAGS = [TITLE_TAG_NAME, ARTIST_TAG_NAME, ALBUM_NAME_TAG_NAME, ALBUM_COVER_TAG_NAME, TRACK_NUMBER_TAG_NAME,
                  TRACK_YEAR_TAG_NAME, DISC_NUM_TAG_NAME]

SPOTIFY_API_URL = 'https://api.spotify.com/v1/search'
SPOTIFY_TOKEN_URL = 'https://accounts.spotify.com/api/token'
