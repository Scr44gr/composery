from threading import get_ident
from typing import Dict, Literal

from av import open as av_open
from av.container import InputContainer

READERS: Dict[str, InputContainer] = {}


def get_reader_id(path: str, mode: Literal["video", "audio"]) -> str:
    """Get the reader id for a given path and mode

    Args:
        path (str): The path to the file
        mode (Literal["video", "audio"]): The mode

    Returns:
        str: The reader id
    """
    assert mode in ["video", "audio"], "Mode must be 'video' or 'audio'"
    thread_id = get_ident()
    reader_id = f"{path}-{mode}-{thread_id}"
    if reader_id not in READERS:
        READERS[reader_id] = av_open(path, "r")
    return reader_id


def free() -> None:
    """Free all readers."""
    for reader in READERS.values():
        reader.close()
    READERS.clear()
