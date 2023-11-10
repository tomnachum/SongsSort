from dtos.spotify_response import TrackObject
from entities.track import TrackEntity


def track_dto_to_entity(track_dto: TrackObject) -> TrackEntity:
    track_dto_dict = track_dto.model_dump()
    print(track_dto_dict)
    track_dto_dict['album']['track_number'] = track_dto_dict['track_number']
    print(track_dto_dict)
    return TrackEntity(**track_dto_dict)
