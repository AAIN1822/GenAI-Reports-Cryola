import os
import base64
import aiohttp
from typing import Optional
from pathlib import Path
from azure.storage.blob import BlobServiceClient, ContentSettings
# from app.core.config import settings # Use local config for now if global not available/ready
from app.ai.multi_angle.config import product_config as config
from app.ai.multi_angle.logger import get_logger
from app.core.config import settings
from azure.identity import DefaultAzureCredential

logger = get_logger("MultiAngle_Storage")

class BlobManager:
    """
    Priority:
    1. Azure Blob (if Credentials exist)
    2. Local Filesystem (Fallback)
    """
    def __init__(self):
        self.logger = get_logger("MultiAngle_Storage")
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
            config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

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
            path = config.OUTPUT_DIR / file_name
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "wb") as f:
                f.write(image_data)
            return f"file://{path.resolve()}"
        else:
            try:
                blob_client = self.container_client.get_blob_client(file_name)
                content_settings = ContentSettings(content_type=content_type)
                blob_client.upload_blob(image_data, overwrite=True, content_settings=content_settings)
                return f"{self.account_url}/{self.container_name}/{file_name}"
            except Exception as e:
                logger.exception(f"Failed upload to Azure Blob: {e}")
                return None

    def upload_file(self, local_path: str, blob_name: str,  content_type="text/plain") -> Optional[str]:
        """
        Upload a local file path to blob. Returns URL on success, None on failure.
        """
        if self.use_local:
            logger.info("Local mode: skipping upload_file() to Azure")
            return None
        try:
            with open(local_path, "rb") as f:
                data = f.read()
            return self.upload_bytes(data, blob_name, content_type=content_type)
        except Exception as e:
            logger.exception(f"upload_file failed: {e}")
            return None
