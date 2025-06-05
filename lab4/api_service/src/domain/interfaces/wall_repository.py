from abc import ABC, abstractmethod
from typing import List
from ..entities.wall_post import WallPost

class WallRepository(ABC):
    @abstractmethod
    def create_post(self, post: WallPost) -> WallPost:
        pass

    @abstractmethod
    def get_all_posts(self) -> List[WallPost]:
        pass 