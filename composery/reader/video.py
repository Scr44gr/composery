from logging import getLogger
from threading import get_ident
from typing import Optional, cast

from av import open as av_open
from av.video.frame import VideoFrame

from . import READERS
from .utils import seek_frame

logger = getLogger()


def get_frame_from_video(video_path: str, time: float) -> Optional[VideoFrame]:
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
    video_stream = READERS[reader_id].streams.video[0]
    frame = seek_frame(READERS[reader_id], video_stream, time)
    assert (
        isinstance(frame, VideoFrame) or frame is None
    ), "Frame is not a VideoFrame instance"
    return frame
