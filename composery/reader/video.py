from threading import get_ident
from typing import Optional

from av import open as av_open
from av.container import InputContainer
from PIL import Image

from . import READERS


def seek_frame(container: InputContainer, frame_index: int) -> Optional[Image.Image]:
    """Seek to a frame in a video file.
    Args:
        container (av.container): The av.container object
        frame_number (int): The frame number
    """
    video_stream = container.streams.video[0]
    assert video_stream.time_base
    assert video_stream.average_rate
    frame_pts = (
        frame_index
        * 1
        / float(video_stream.average_rate)
        * float(video_stream.time_base)
        * 1_000_000
    )
    try:
        for frame in container.decode(video_stream):
            if int(frame_pts) >= frame.pts or int(frame.pts) <= frame.pts:
                return frame.to_image()
    except:
        # raise IndexError(f"Frame number {frame_index} is out of bounds")
        return


def get_frame_from_video(video_path: str, frame_index: int) -> Optional[Image.Image]:
    """Get a frame from a video file.

    Args:
        video_path (str): The path to the video file
        frame_index (int): The frame number

    Returns:
        Image.Image: The frame image
    Raises:
        IndexError: If the frame number is out of bounds
    """
    thread_id = get_ident()
    reader_id = f"{video_path}-video-{thread_id}"
    if reader_id not in READERS:
        READERS[reader_id] = av_open(video_path, "r")

    return seek_frame(READERS[reader_id], frame_index)
