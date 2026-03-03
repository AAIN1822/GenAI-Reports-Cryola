# compression.py
from PIL import Image
from io import BytesIO
from PIL import ImageOps
import requests
from app.core.config import settings
from azure.storage.blob import BlobServiceClient
from azure.identity import DefaultAzureCredential


AZURE_STORAGE_ACCOUNT_NAME = settings.AZURE_STORAGE_ACCOUNT_NAME
AZURE_STORAGE_ACCOUNT_KEY = settings.AZURE_STORAGE_ACCOUNT_KEY
AZURE_BLOB_CONTAINER = settings.AZURE_BLOB_CONTAINER_NAME

#credential=AZURE_STORAGE_ACCOUNT_KEY
credential = DefaultAzureCredential()

blob_service_client = BlobServiceClient(
    account_url=f"https://{AZURE_STORAGE_ACCOUNT_NAME}.blob.core.windows.net",
    credential=credential
)

# image compression logic
def compress_image_in_memory(
    image_bytes: bytes,
    target_bytes: int,
    max_dimension: int,
    max_colors: int = 256,
    optimize: bool = True,
) -> bytes:
    """
    In-memory image compression:
    - JPEG: quality reduction
    - PNG: quantization + alpha preservation
    """
    original_size_mb = len(image_bytes) / (1024 * 1024)
    target_mb = target_bytes / (1024 * 1024)
    print(f"Original size: {original_size_mb:.2f} MB")

    img = Image.open(BytesIO(image_bytes))
    img = ImageOps.exif_transpose(img)
    fmt = (img.format or "JPEG").upper()

    width, height = img.size
    max_side = max(width, height)

    if max_side > max_dimension:
        scale = max_dimension / max_side
        new_size = (
            int(width * scale),
            int(height * scale)
        )
        print(f"Resizing from {img.size} → {new_size}")
        img = img.resize(new_size, Image.Resampling.LANCZOS)

    # Skip if already below target
    if len(image_bytes) <= target_bytes:
        print("Already below target, skipping")
        return image_bytes

    # JPEG HANDLING
    if fmt in ("JPEG", "JPG"):
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        output = BytesIO()
        quality = 95
        best_bytes = image_bytes
        while quality >= 10:
            output.seek(0)
            output.truncate(0)
            img.save(
                output,
                format="JPEG",
                quality=quality,
                optimize=optimize
            )
            size_mb = output.tell() / (1024 * 1024)
            print(f"Quality={quality} → {size_mb:.2f} MB")
            best_bytes = output.getvalue()
            if output.tell() <= target_bytes:
                print(f"Target achieved at quality={quality}")
                return best_bytes

            quality -= 10
        print("Target not achieved, returning best effort")
        return best_bytes

    # PNG HANDLING
    if fmt == "PNG":
        MEDIANCUT = 0
        source_img = img
        current_colors = max_colors
        best_bytes = image_bytes
        while current_colors >= 16:
            output = BytesIO()
            if source_img.mode in ("RGBA", "LA"):
                alpha = source_img.getchannel("A")
                img_rgb = source_img.convert("RGB")
                img_quant = img_rgb.quantize(
                    colors=current_colors,
                    method=MEDIANCUT
                )
                img_quant = img_quant.convert("RGBA")
                img_quant.putalpha(alpha)
            else:
                img_quant = source_img.quantize(
                    colors=current_colors,
                    method=MEDIANCUT
                )
            img_quant.save(
                output,
                format="PNG",
                optimize=optimize
            )
            size_mb = output.tell() / (1024 * 1024)
            print(f"Colors={current_colors} → {size_mb:.2f} MB")
            best_bytes = output.getvalue()
            if output.tell() <= target_bytes:
                print(f"Target achieved with {current_colors} colors")
                return best_bytes

            current_colors = max(16, current_colors // 2)
        print("Target not achieved, returning best effort")
        return best_bytes

    # FALLBACK (unknown formats)
    print("Unsupported format, returning original")
    return image_bytes


# blob_helpers
def copy_blob_with_compression_if_needed(
    source_url: str,
    target_folder: str
) -> str:
    """
    - Downloads image into memory
    - Compresses if > 20 MB
    - Uploads to project folder
    """
    container = blob_service_client.get_container_client(AZURE_BLOB_CONTAINER)

    file_name = source_url.split("?")[0].split("/")[-1]
    destination_path = f"project/{target_folder}/{file_name}"

    r = requests.get(source_url, timeout=30)
    r.raise_for_status()
    image_bytes = r.content
    if len(image_bytes) > settings.MAX_IMAGE_SIZE_MB * 1024 * 1024:
        image_bytes = compress_image_in_memory(
            image_bytes,
            settings.MAX_IMAGE_SIZE_MB * 1024 * 1024,
            max_dimension=settings.MAX_IMAGE_DIMENSION
        )
    blob = container.get_blob_client(destination_path)
    blob.upload_blob(image_bytes, overwrite=True)
    return blob.url
