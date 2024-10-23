from typing import Optional, cast

from av.video.frame import VideoFrame

from . import READERS, get_reader_id
from .utils import seek_frame


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
    reader_id = get_reader_id(video_path, mode="video")
    video_stream = READERS[reader_id].streams.video[0]
    frame = seek_frame(READERS[reader_id], video_stream, time)
    assert (
        isinstance(frame, VideoFrame) or frame is None
    ), "Frame is not a VideoFrame instance"
    return frame


def get_video_size(video_path: str) -> tuple[int, int]:
    """Get the size of a video file.

    Args:
        video_path (str): The path to the video file

    Returns:
        tuple[int, int]: The width and height of the video
    """
    reader_id = get_reader_id(video_path, mode="video")
    video_stream = READERS[reader_id].streams.video[0]
    return cast(tuple[int, int], (video_stream.width, video_stream.height))
