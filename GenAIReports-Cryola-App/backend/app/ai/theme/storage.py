import os
import base64
import aiohttp
from typing import Optional
from pathlib import Path
from azure.storage.blob import BlobServiceClient, ContentSettings
from azure.identity import DefaultAzureCredential
from app.core.config import settings
from .config import Config
from .logger import get_logger
from .logger import get_current_log_filepath

logger = get_logger("ThemeEngine_Storage")

def encode_bytes_to_base64(image_bytes: bytes, mime_type: str = "image/jpeg") -> str:
    b64_string = base64.b64encode(image_bytes).decode("utf-8")
    return f"data:{mime_type};base64,{b64_string}"

class BlobManager:
    """
    Priority:
    1. Azure Blob (if Credentials exist)
    2. Local Filesystem (Fallback)
    """
    def __init__(self):
        self.logger = get_logger("ThemeEngine_Storage")
        self.account_name = settings.AZURE_STORAGE_ACCOUNT_NAME
        #self.account_key = settings.AZURE_STORAGE_ACCOUNT_KEY
        self.account_key = DefaultAzureCredential()
        self.container_name = settings.AZURE_BLOB_CONTAINER_NAME
        
        # Determine Mode
        if self.account_name and self.account_key:
            self.use_local = False
            self.account_url = f"https://{self.account_name}.blob.core.windows.net"
            try:
                self.blob_service_client = BlobServiceClient(
                    account_url=self.account_url,
                    credential=self.account_key
                )
                self.container_client = self.blob_service_client.get_container_client(self.container_name)
                # Note: In prod, maybe we dont need to check exists every time to save latency
                if not self.container_client.exists():
                    self.container_client.create_container()
            except Exception as e:
                logger.error(f"Azure Connection failed, falling back to local: {e}")
                self.use_local = True
        else:
            self.use_local = True

        if self.use_local:
            Config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    async def download_image_to_bytes(self, url: str) -> bytes:
        """Handles http/https URLs or local file paths"""
        if url.startswith("http"):
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    resp.raise_for_status()
                    return await resp.read()
        else:
            # Assume local path or file://
            path = url.replace("file://", "")
            if not os.path.exists(path): raise FileNotFoundError(f"Local input not found: {path}")
            with open(path, "rb") as f: return f.read()

    def upload_bytes(self, image_data: bytes, file_name: str, content_type="application/octet-stream") -> Optional[str]:
        """
        Upload raw bytes. Returns URL on success, None on failure.
        """
        if self.use_local:
            path = Config.OUTPUT_DIR / file_name
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "wb") as f:
                f.write(image_data)
            return f"file://{path.resolve()}"
        else:
            try:
                blob_client = self.container_client.get_blob_client(file_name)
                blob_client.upload_blob(image_data, overwrite=True)
                blob_client.set_http_headers(
                    content_settings=ContentSettings(
                        content_type=content_type,
                        content_disposition=f'attachment; filename="{os.path.basename(file_name)}"'
                    )
                )
                return f"{self.account_url}/{self.container_name}/{file_name}"
            except Exception as e:
                logger.exception(f"Failed upload to Azure Blob: {e}")
                return None
           
    def append_project_log(self, folder_name: str, log_text: str) -> str:    
        def clean(x):
            return str(x).replace(" ", "_").replace("/", "_").replace("\\", "_")
        
        file_name = f"{clean(folder_name)}.txt"
        blob_path = f"project/{folder_name}/{file_name}"
        blob_client = self.container_client.get_blob_client(blob_path)
        if not blob_client.exists():
            blob_client.create_append_blob()
        else:
            print("Append blob already exists")

        blob_client.append_block((log_text + "\n").encode("utf-8"))
        return f"{self.account_url}/{self.container_name}/{blob_path}"
