import os
import io
import mimetypes
import base64
from datetime import datetime
from PIL import Image
from typing import Tuple, Union
from pathlib import Path

def encode_image(path_or_bytes: Union[str, bytes]) -> str:
    """
    Encodes an image to a data URL string.
    Accepts either a file path (str) or raw bytes.
    """
    if isinstance(path_or_bytes, bytes):
        b64 = base64.b64encode(path_or_bytes).decode("utf-8")
        # Default to png if bytes are passed without context, or detection logic could be added
        mime = "image/png" 
        return f"data:{mime};base64,{b64}"
    
    path = path_or_bytes
    mime, _ = mimetypes.guess_type(path)
    if not mime:
        mime = "image/png"
    
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    return f"data:{mime};base64,{b64}"

def encode_bytes_to_base64(image_bytes: bytes, mime_type: str = "image/jpeg") -> str:
    b64_string = base64.b64encode(image_bytes).decode("utf-8")
    return f"data:{mime_type};base64,{b64_string}"


def load_image_file(path: str) -> Tuple[str, bytes]:
    """
    Returns a tuple (filename, bytes) required by OpenAI client for image uploads.
    Ensures correct MIME type by using the actual file extension.
    """
    filename = os.path.basename(path)
    with open(path, "rb") as f:
        return (filename, f.read()) 

def load_image_from_bytes(data: bytes, filename: str) -> Tuple[str, bytes]:
    """
    Wrapper to return (filename, bytes) from raw data.
    """
    return (filename, data)

def make_output_filename(step: str, base_shelf_filename: str, version: int):
    base_name = os.path.splitext(os.path.basename(base_shelf_filename))[0]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"graphics_{step}_{base_name}_{timestamp}_v{version}.png"

def as_data_url(path: str) -> str:
    """
    Reads a local file and converts it to a data:image/png;base64 URL,
    which is accepted by Azure OpenAI ChatCompletion (O3).
    """
    return encode_image(path)
