from azure.storage.blob import BlobServiceClient
from azure.identity import DefaultAzureCredential
from app.core.config import settings
 
# -----------------------------
# Helpers
# -----------------------------
def clean(x):
            return str(x).replace(" ", "_").replace("/", "_").replace("\\", "_")

def clean_filename(name: str) -> str:
    if name.startswith("project_"):
        name = name[len("project_"):]

    name = name.replace("_.txt", ".txt")
    return name


# ---------------------------------
# Copy folder (preserve blob type)
# ---------------------------------
def copy_folder(old_folder: str, new_folder: str):
    AZURE_STORAGE_ACCOUNT_NAME = settings.AZURE_STORAGE_ACCOUNT_NAME
    AZURE_STORAGE_ACCOUNT_KEY = settings.AZURE_STORAGE_ACCOUNT_KEY
    AZURE_BLOB_CONTAINER = settings.AZURE_BLOB_CONTAINER_NAME
 
    #credential=AZURE_STORAGE_ACCOUNT_KEY
    credential = DefaultAzureCredential()
   
    blob_service_client = BlobServiceClient(
        account_url=f"https://{AZURE_STORAGE_ACCOUNT_NAME}.blob.core.windows.net",
        credential=credential,
    )
    container_client = blob_service_client.get_container_client(AZURE_BLOB_CONTAINER)
    new_paths = []
    blobs = container_client.list_blobs(name_starts_with=old_folder)
    for blob in blobs:
        source_blob = container_client.get_blob_client(blob.name)
        # replace folder prefix
        new_blob_name = blob.name.replace(old_folder, new_folder, 1)

        filename = blob.name.split("/")[-1]
        old_file_name = clean_filename(f"{clean(old_folder)}.txt")
        new_file_name = clean_filename(f"{clean(new_folder)}.txt")
        
        if filename == old_file_name:
            new_blob_name = "/".join(
                new_blob_name.split("/")[:-1] + [new_file_name]
            )

        dest_blob = container_client.get_blob_client(new_blob_name)
        
        # Preserve blob type
        props = source_blob.get_blob_properties()
        blob_type = props.blob_type
        if blob_type == "AppendBlob":
            dest_blob.create_append_blob()

        elif blob_type == "PageBlob":
            dest_blob.create_page_blob(size=props.size)

        source_url = source_blob.url
        dest_blob.start_copy_from_url(source_url)
        new_paths.append(new_blob_name)
    return new_paths
