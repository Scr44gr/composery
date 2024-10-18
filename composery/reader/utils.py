from logging import getLogger
from typing import Optional, Union

from av.audio.frame import AudioFrame
from av.audio.stream import AudioStream
from av.container import InputContainer
from av.subtitles.subtitle import SubtitleSet
from av.video.frame import VideoFrame
from av.video.stream import VideoStream

logger = getLogger()


def get_frame_time(
    frame: Union[AudioFrame, VideoFrame], stream: Union[AudioStream, VideoStream]
) -> float:
    """Get the time of a frame in milliseconds.
    Args:
        frame (av.AudioFrame): The audio frame
        video_stream (av.Video
    """
    assert frame.pts is not None, "Frame does not have a pts"
    return float(frame.pts or 1 / stream.frames)


def seek_frame(
    container: InputContainer, stream: Union[AudioStream, VideoStream], time: float
) -> Optional[Union[AudioFrame, VideoFrame]]:
    """Seek to a frame in a video file.
    Args:
        container (av.container): The av.container object
        stream: The stream object
        time: The time in seconds
    """

    try:
        for frame in container.decode(stream):
            assert not isinstance(frame, SubtitleSet)
            if get_frame_time(frame, stream) >= time:
                return frame
    except Exception as error:
        logger.error(f"Error seeking frame: {error}")
        return


__all__ = ["seek_frame", "get_frame_time"]
