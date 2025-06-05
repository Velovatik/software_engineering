from typing import List
from ...domain.entities.wall_post import WallPost
from ...domain.interfaces.wall_repository import WallRepository

class WallUseCases:
    def __init__(self, wall_repository: WallRepository):
        self.wall_repository = wall_repository

    def create_post(self, post: WallPost) -> WallPost:
        return self.wall_repository.create_post(post)

    def get_all_posts(self) -> List[WallPost]:
        return self.wall_repository.get_all_posts() 