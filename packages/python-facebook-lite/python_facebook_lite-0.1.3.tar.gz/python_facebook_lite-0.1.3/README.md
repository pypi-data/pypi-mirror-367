# PythonFacebook

A lightweight Python library for interacting with the Facebook Graph API to manage page content.

## Installation

```bash
pip install pythonfacebook
```

## Features

- Post text messages to Facebook pages
- Upload images with captions
- Upload videos
- Post comments on existing posts
- Robust error handling

## Quick Start

```python
from pythonfacebook import Facebook

# Initialize with your Page ID and Access Token
fb = Facebook(page_id="your_page_id", access_token="your_access_token")

# Post a text message
fb.create_text_post("Hello, world!")

# Post an image
fb.create_image_post(
    post_text="Check out this image!", 
    image_paths=["/path/to/image.jpg"]
)

# Post a video
fb.create_video_post(
    video_path="/path/to/video.mp4", 
    title="My Video", 
    description="Video description"
)

# Post a comment
fb.create_comment(post_id="facebook_post_id", comment="Nice post!")
```

## Authentication

You'll need:
- A Facebook Page ID
- A valid Access Token with appropriate permissions

## Methods

- `create_text_post(text, url=None)`: Post text to your page
- `create_image_post(post_text, image_paths)`: Post images with text
- `create_video_post(video_path, title=None, description=None)`: Upload a video
- `create_comment(post_id, comment)`: Comment on a post

## Error Handling

Methods return `None` if a request fails and log errors.

## Requirements

- Python 3.10+
- `requests` library

## Contributing

Contributions welcome! Submit pull requests or open issues.

## License

MIT License

## Disclaimer

Not officially affiliated with Facebook. Use according to Facebook's API terms of service.
