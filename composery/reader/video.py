import imageio
from numpy import ndarray
from PIL import Image

READERS = {}


def get_frame_from_video(video_path: str, frame_number: int) -> ndarray:
    """Get a frame from a video file.

    Args:
        video_path (str): The path to the video file
        frame_number (int): The frame number

    Returns:
        ndarray: The frame as a NumPy array
    Raises:
        IndexError: If the frame number is out of bounds
    """
    if video_path not in READERS:
        READERS[video_path] = imageio.get_reader(video_path)

    return READERS[video_path].get_data(frame_number)


def free() -> None:
    """Free all video readers."""
    for reader in READERS.values():
        reader.close()
    READERS.clear()
