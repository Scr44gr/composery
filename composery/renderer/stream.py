from fractions import Fraction
from typing import TypeVar, Union, cast

from av.audio.frame import AudioFrame
from av.audio.stream import AudioStream
from av.container import OutputContainer
from av.video.frame import VideoFrame
from av.video.stream import VideoStream

from composery.renderer.options import VideoWriterOptions

Frame = Union[VideoFrame, AudioFrame]

T = TypeVar("T", VideoStream, AudioStream)


def create_stream(
    stream_type: type[T], container: OutputContainer, options: VideoWriterOptions
) -> T:
    """Create a setup stream for the av output container"""
    if stream_type == VideoStream:
        video_stream = container.add_stream(
            codec_name=options.codec,
            rate=options.framerate,
            options={
                "crf": str(options.crf),
                "preset": options.preset.value,
                "pix_fmt": options.pixel_format.value,
            },
        )
        video_stream.width = options.width
        video_stream.height = options.height
        video_stream.thread_type = "AUTO"
        video_stream.codec_context.time_base = Fraction(1, options.framerate)
        video_stream.bit_rate = int(options.bitrate[:-1]) * 1000
        return cast(T, video_stream)

    assert isinstance(stream_type, AudioStream), "Invalid stream type"
    audio_stream = container.add_stream(
        options.audio_codec,
        rate=options.audio_sample_rate,
    )
    audio_stream.codec_context.time_base = Fraction(1, options.audio_sample_rate)
    audio_stream.bit_rate = int(options.audio_bitrate[:-1]) * 1000
    return cast(T, audio_stream)
