from abc import ABC, abstractmethod
from typing import List, Optional
from ..entities.wall_post import WallPost

class WallRepository(ABC):
    @abstractmethod
    def create(self, wall_post: WallPost) -> WallPost:
        pass

    @abstractmethod
    def get_by_id(self, post_id: int) -> Optional[WallPost]:
        pass

    @abstractmethod
    def get_by_user_id(self, user_id: int) -> List[WallPost]:
        pass

    @abstractmethod
    def get_all(self) -> List[WallPost]:
        pass

    @abstractmethod
    def update(self, wall_post: WallPost) -> Optional[WallPost]:
        pass

    @abstractmethod
    def delete(self, post_id: int) -> bool:
        pass 