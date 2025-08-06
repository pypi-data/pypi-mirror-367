import logging
import os
from typing import Any

import requests

from .endpoints import Endpoints
from .enums import Messages

logger = logging.getLogger(__name__)


class Facebook:
    """A class for posting content to a Facebook page."""

    def __init__(self, page_id: str, access_token: str) -> None:
        """Initializes a Facebook object with the ID
        of the Facebook page and its access token.

        Args:
            page_id (str): The ID of the Facebook page.
            access_token (str): The access token of the Facebook page.
        """
        self.PAGE_ID = page_id
        self.ACCESS_TOKEN = access_token
        self.endpoints = Endpoints(self.PAGE_ID)

    def _make_request(
        self,
        endpoint: str,
        method: str = "POST",
        files: dict | None = None,
        data: dict[str, Any] | None = None,
        error_message: str = Messages.REQUEST_FAILED,
    ) -> dict[str, str] | None:
        """
        Centralized method to handle all API requests.

        Args:
            endpoint (str): The API endpoint to send the request to
            method (str): HTTP method to use (default: "POST")
            files (dict | None): Files to upload
            data (dict[str, any] | None): Data payload for the request
            error_message (str): Custom error message for logging

        Returns:
            dict[str, str] | None: JSON response from the API or None if request fails
        """
        data = data or {}
        data["access_token"] = self.ACCESS_TOKEN

        try:
            response = requests.request(
                method=method, url=endpoint, files=files, data=data
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"{error_message}: {str(e)}")
            return None

    def _upload_image(
        self, image_path: str, image_description: str | None = None
    ) -> dict[str, str] | None:
        """
        Uploads an image to Facebook.

        Args:
            image_path (str): Image path to be uploaded.
            image_description (str | None, optional): Image description.
            Defaults to None.

        Returns:
            dict[str, str] | None: JSON response from the API or None if request fails.
        """
        data = {
            "message": image_description,
            "published": False,
        }

        files = None
        if os.path.isfile(image_path):
            files = {"file": open(image_path, "rb")}
        else:
            data["url"] = image_path

        return self._make_request(
            endpoint=self.endpoints.photos,
            files=files,
            data=data,
            error_message=Messages.ERROR_UPLOAD_IMAGE,
        )

    def create_image_post(
        self, post_text: str, image_paths: list[str]
    ) -> dict[str, str] | None:
        """
        Creates a post with text and image(s) on the Facebook page.

        Args:
            post_text (str): Text to be posted on Facebook.
            image_paths (list[str]): Image paths to be uploaded.

        Returns:
            dict[str, str] | None: JSON response from the API or None if request fails.
        """
        data = {"message": post_text}

        image_ids = []
        for image_path in image_paths:
            uploaded_image = self._upload_image(image_path)
            if uploaded_image and uploaded_image.get("id"):
                image_ids.append(uploaded_image["id"])

        if image_ids:
            for index, image_id in enumerate(image_ids):
                data[f"attached_media[{index}]"] = f"{{'media_fbid': '{image_id}'}}"

        return self._make_request(
            endpoint=self.endpoints.feed,
            data=data,
            error_message=Messages.ERROR_POST_IMAGE,
        )

    def create_video_post(
        self, video_path: str, title: str | None = None, description: str | None = None
    ) -> dict[str, str] | None:
        """
        Creates a video post with a title and description.

        Args:
            video_path (str): Video path to be uploaded.
            title (str | None, optional): Video title. Defaults to None.
            description (str | None, optional): Video description. Defaults to None.

        Returns:
            dict[str, str] | None: JSON response from the API or None if request fails.
        """
        files = {"file": open(video_path, "rb")}
        data = {
            "title": title,
            "description": description,
        }

        return self._make_request(
            endpoint=self.endpoints.videos,
            files=files,
            data=data,
            error_message=Messages.ERROR_POST_VIDEO,
        )

    def create_text_post(
        self, text: str, url: str | None = None
    ) -> dict[str, str] | None:
        """
        Creates a text post, optionally with a URL.

        Args:
            text (str): Text to be posted on Facebook.
            url (str | None, optional): URL to be included in the post.
            Defaults to None.

        Returns:
            dict[str, str] | None: JSON response from the API or None if request fails.
        """
        data = {"message": text, "link": url}

        return self._make_request(
            endpoint=self.endpoints.feed,
            data=data,
            error_message=Messages.ERROR_POST_TEXT,
        )

    def create_comment(self, post_id: str, comment: str) -> dict[str, str] | None:
        """
        Posts a comment on a Facebook post.

        Args:
            post_id (str): ID of the Facebook post.
            comment (str): Comment to be posted.

        Returns:
            dict[str, str] | None: JSON response from the API or None if request fails.
        """
        return self._make_request(
            endpoint=self.endpoints.comments(post_id),
            data={"message": comment},
            error_message=Messages.ERROR_POST_COMMENT,
        )
