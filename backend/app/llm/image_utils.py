"""Shrink and encode an image so it fits the vision model's request limits."""

import base64
import io

from PIL import Image

MAX_SIDE = 1024
MAX_BYTES = 4 * 1024 * 1024


def to_data_url(image_bytes: bytes) -> str:
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    img.thumbnail((MAX_SIDE, MAX_SIDE))
    for quality in (85, 70, 55):
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=quality)
        data = buffer.getvalue()
        if len(data) <= MAX_BYTES:
            break
    return "data:image/jpeg;base64," + base64.b64encode(data).decode("ascii")
