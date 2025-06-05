from typing import List
from ...domain.interfaces.wall_repository import WallRepository
from ...domain.entities.wall_post import WallPost

class InMemoryWallRepository(WallRepository):
    def __init__(self):
        self.posts: List[WallPost] = []

    def create_post(self, post: WallPost) -> WallPost:
        post.id = len(self.posts)
        self.posts.append(post)
        return post

    def get_all_posts(self) -> List[WallPost]:
        return self.posts 