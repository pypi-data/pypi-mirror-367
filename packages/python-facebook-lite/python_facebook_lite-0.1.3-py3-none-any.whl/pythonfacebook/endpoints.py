"""
Facebook endpoints
"""


class Endpoints:
    """Class for building Facebook endpoints"""

    VERSION = "v18.0"
    GRAPH = "https://graph.facebook.com"
    GRAPH_VIDEO = "https://graph-video.facebook.com"

    def __init__(self, page_id: str) -> None:
        if not page_id:
            raise ValueError("Page ID cannot be empty.")
        self.page_id = page_id

    @property
    def feed(self) -> str:
        """Endpoint for page feed"""
        return f"{self.GRAPH}/{self.VERSION}/{self.page_id}/feed"

    @property
    def photos(self) -> str:
        """Endpoint for page photos"""
        return f"{self.GRAPH}/{self.VERSION}/{self.page_id}/photos"

    @property
    def videos(self) -> str:
        """Endpoint for page videos"""
        return f"{self.GRAPH_VIDEO}/{self.VERSION}/{self.page_id}/videos"

    def comments(self, post_id: str) -> str:
        """Endpoint for comments on a specific post"""
        if not post_id:
            raise ValueError("Post ID cannot be empty.")
        return f"{self.GRAPH}/{self.VERSION}/{post_id}/comments"
