from dtos.spotify_response import TrackObject
from entities.track import TrackEntity


def track_dto_to_entity(track_dto: TrackObject) -> TrackEntity:
    track_dto_dict = track_dto.model_dump()
    track_dto_dict['album']['track_number'] = track_dto_dict['track_number']
    return TrackEntity(**track_dto_dict)
