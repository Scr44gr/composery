from typing import Dict

from av.container import InputContainer

READERS: Dict[str, InputContainer] = {}


def free() -> None:
    """Free all readers."""
    for reader in READERS.values():
        reader.close()
    READERS.clear()
