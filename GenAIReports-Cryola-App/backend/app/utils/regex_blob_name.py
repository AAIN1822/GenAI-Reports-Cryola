import re
 
SAFE_BLOB_REGEX = re.compile(r'[^a-zA-Z0-9._/-]')
 
def sanitize_blob_name(name: str) -> str:
    """
    Converts an arbitrary string into a safe Azure blob name.
    - Replaces unsafe characters with '_'
    - Collapses multiple underscores
    - Strips leading/trailing slashes
    """
 
    # Replace unsafe chars
    name = SAFE_BLOB_REGEX.sub('_', name)
 
    # Collapse multiple underscores
    name = re.sub(r'_+', '_', name)
 
    # Remove leading/trailing slashes
    name = name.strip('/')
 
    return name