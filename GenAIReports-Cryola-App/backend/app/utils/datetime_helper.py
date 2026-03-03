from datetime import datetime, UTC

def utc_now(as_iso: bool = False):
    dt = datetime.now(UTC)
    return dt.isoformat() if as_iso else dt

def utc_unix():
    return int(datetime.now(UTC).timestamp())