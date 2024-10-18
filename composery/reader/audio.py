from logging import getLogger
from threading import get_ident
from typing import Optional

import av
from av.container import InputContainer

from . import READERS
from .utils import get_frame_time

logger = getLogger()


def seek_audio_frame(container: InputContainer, time: float) -> Optional[av.AudioFrame]:
    """Seek to an audio frame in a video file.
    Args:
        container (av.container): The av.container object
        time: The time in seconds
    """
    audio_stream = container.streams.audio[0]
    assert audio_stream.time_base

    try:
        for frame in container.decode(audio_stream):
            if get_frame_time(frame, audio_stream) >= time:
                return frame
    except Exception as error:
        logger.error(f"Error seeking audio frame: {error}")
        return


def get_audio_frame_from_video(video_path: str, time: float) -> Optional[av.AudioFrame]:
    """Get an audio frame from a video file.

    Args:
        video_path (str): The path to the video file
        frame_index (int): The frame number
    Returns:
        av.AudioFrame: The audio frame
    Raises:
        IndexError: If the frame number is out of bounds
    """
    thread_id = get_ident()
    reader_id = f"{video_path}-audio-{thread_id}"
    if reader_id not in READERS:
        READERS[reader_id] = av.open(video_path, "r")

    return seek_audio_frame(READERS[reader_id], time)
