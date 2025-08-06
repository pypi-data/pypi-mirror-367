"""
Facebook enumerations
"""

from enum import Enum


class Messages(str, Enum):
    """
    Facebook Error Messages
    """

    ERROR_POST_TEXT = "Error posting text to Facebook"
    ERROR_POST_IMAGE = "Error posting image(s) to Facebook"
    ERROR_POST_VIDEO = "Error posting video to Facebook"
    ERROR_POST_COMMENT = "Error posting comment to Facebook"
    ERROR_UPLOAD_IMAGE = "Error uploading image(s) to Facebook"
    REQUEST_FAILED = "Request failed"
