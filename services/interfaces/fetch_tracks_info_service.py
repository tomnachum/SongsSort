from abc import ABC, abstractmethod
from typing import List
from entities.track import TrackEntity


class FetchTracksInfoService(ABC):

    @abstractmethod
    def get_tracks(self, artist: str, track: str) -> List[TrackEntity]:
        pass
