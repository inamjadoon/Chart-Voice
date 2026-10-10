import base64

def encode_image_to_base64(image_path: str) -> str:
    """
    Reads an image file from disk and encodes it into a base64 string 
    so it can be sent to Groq's vision models.
    """
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def image_bytes_to_base64(image_bytes: bytes) -> str:
    """
    Encodes raw image bytes (e.g. from a FastAPI UploadFile) into a base64 string.
    """
    return base64.b64encode(image_bytes).decode('utf-8')