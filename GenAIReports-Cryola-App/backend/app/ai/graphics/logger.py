import os
import sys
import logging
import threading

# Global context for threading
_context = threading.local()

def set_log_context(project_id="", account="", structure="", sub_brand="", season="", campaign_name=""):
    """Set metadata fields for this workflow."""
    _context.project_id = project_id
    _context.account = account
    _context.structure = structure
    _context.sub_brand = sub_brand
    _context.season = season
    _context.campaign_name = campaign_name

def _get_log_filename():
    """Returns a unique log file path based on context."""
    project_id = getattr(_context, "project_id", "Unknown")
    account = getattr(_context, "account", "Unknown")
    structure = getattr(_context, "structure", "Unknown")
    sub_brand = getattr(_context, "sub_brand", "Unknown")
    season = getattr(_context, "season", "Unknown")
    campaign_name = getattr(_context, "campaign_name", "Unknown")

    def clean(x):  
        return str(x).replace(" ", "").replace("/", "_")

    filename = (
        f"{clean(project_id)}"
        f"{clean(account)}_"
        f"{clean(structure)}_"
        f"{clean(sub_brand)}_"
        f"{clean(season)}_"
        f"{clean(campaign_name)}.log"
    )

    os.makedirs("logs", exist_ok=True)
    return os.path.join("logs", filename)

def get_current_log_filepath():
    """Helper to expose the current log path for uploading."""
    return _get_log_filename()

class ContextFilter(logging.Filter):
    """Inject values into every log record."""
    def filter(self, record):
        record.project_id = getattr(_context, "project_id", "")
        record.account = getattr(_context, "account", "")
        record.structure = getattr(_context, "structure", "")
        record.sub_brand = getattr(_context, "sub_brand", "")
        record.season = getattr(_context, "season", "")
        record.campaign_name = getattr(_context, "campaign_name", "")
        return True

def get_logger(name: str):
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    log_format = (
        "%(asctime)s | %(project_id)s | %(account)s | %(structure)s | %(sub_brand)s | "
        "%(season)s | %(campaign_name)s | %(levelname)s | %(message)s"
    )
    formatter = logging.Formatter(log_format, datefmt="%Y-%m-%d %H:%M:%S")

    # 1. File Handler (Writes to local disk first)
    file_path = _get_log_filename()
    file_handler = logging.FileHandler(file_path, mode="a", encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    # 2. Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    logger.addFilter(ContextFilter())
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
